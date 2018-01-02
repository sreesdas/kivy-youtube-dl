# -*- coding: utf-8 -*-
"""
This module implements the core developer interface for pytube.

The problem domain of the :class:`YouTube <YouTube> class focuses almost
exclusively on the developer interface. Pytube offloads the heavy lifting to
smaller peripheral modules and functions.

"""
from __future__ import absolute_import

import json
import logging

from pytube import Caption
from pytube import CaptionQuery
from pytube import extract
from pytube import mixins
from pytube import request
from pytube import Stream
from pytube import StreamQuery
from pytube.compat import parse_qsl
from pytube.exceptions import AgeRestrictionError
from pytube.helpers import apply_mixin


logger = logging.getLogger(__name__)


class YouTube(object):
    """Core developer interface for pytube."""

    def __init__(
        self, url=None, defer_prefetch_init=False, on_progress_callback=None,
        on_complete_callback=None,
    ):
        """Construct a :class:`YouTube <YouTube>`.

        :param str url:
            A valid YouTube watch URL.
        :param bool defer_init:
            Defers executing any network requests.
        :param func on_progress_callback:
            (Optional) User defined callback function for stream download
            progress events.
        :param func on_complete_callback:
            (Optional) User defined callback function for stream download
            complete events.

        """
        self.js = None      # js fetched by js_url
        self.js_url = None  # the url to the js, parsed from watch html

        # note: vid_info may eventually be removed. It sounds like it once had
        # additional formats, but that doesn't appear to still be the case.

        self.vid_info = None      # content fetched by vid_info_url
        self.vid_info_url = None  # the url to vid info, parsed from watch html

        self.watch_html = None     # the html of /watch?v=<video_id>
        self.player_config = None  # inline js in the html containing streams

        self.fmt_streams = []  # list of :class:`Stream <Stream>` instances
        self.caption_tracks = []

        # video_id part of /watch?v=<video_id>
        self.video_id = extract.video_id(url)

        # https://www.youtube.com/watch?v=<video_id>
        self.watch_url = extract.watch_url(self.video_id)

        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self.stream_monostate = {
            # user defined callback functions.
            'on_progress': on_progress_callback,
            'on_complete': on_complete_callback,
        }

        if not defer_prefetch_init:
            self.prefetch_init()

    def prefetch_init(self):
        """Download data, descramble it, and build Stream instances.

        :rtype: None

        """
        self.prefetch()
        self.init()

    def init(self):
        """Descramble the stream data and build Stream instances.

        The initialization process takes advantage of Python's
        "call-by-reference evaluation," which allows dictionary transforms to
        be applied in-place, instead of holding references to mutations at each
        interstitial step.

        :rtype: None

        """
        logger.info('init started')

        self.vid_info = {k: v for k, v in parse_qsl(self.vid_info)}
        self.player_config = extract.get_ytplayer_config(self.watch_html)

        config_args = self.player_config['args']

        # https://github.com/nficano/pytube/issues/165
        stream_maps = ['url_encoded_fmt_stream_map']
        if 'adaptive_fmts' in config_args:
            stream_maps.append('adaptive_fmts')

        # unscramble the progressive and adaptive stream manifests.
        for fmt in stream_maps:
            mixins.apply_descrambler(self.vid_info, fmt)
            mixins.apply_descrambler(config_args, fmt)

            # apply the signature to the download url.
            mixins.apply_signature(config_args, fmt, self.js)

            # build instances of :class:`Stream <Stream>`
            self.initialize_stream_objects(fmt)

        # load the player_response object (contains subtitle information)
        apply_mixin(config_args, 'player_response', json.loads)

        self.initialize_caption_objects()
        logger.info('init finished successfully')

    def prefetch(self):
        """Eagerly download all necessary data.

        Eagerly executes all necessary network requests so all other
        operations don't does need to make calls outside of the interpreter
        which blocks for long periods of time.

        :rtype: None

        """
        self.watch_html = request.get(url=self.watch_url)
        if extract.is_age_restricted(self.watch_html):
            raise AgeRestrictionError('Content is age restricted')
        self.vid_info_url = extract.video_info_url(
            video_id=self.video_id,
            watch_url=self.watch_url,
            watch_html=self.watch_html,
        )
        self.js_url = extract.js_url(self.watch_html)
        self.js = request.get(self.js_url)
        self.vid_info = request.get(self.vid_info_url)

    def initialize_stream_objects(self, fmt):
        """Convert manifest data to instances of :class:`Stream <Stream>`.

        Take the unscrambled stream data and uses it to initialize
        instances of :class:`Stream <Stream>` for each media stream.

        :param str fmt:
            Key in stream manifest (``ytplayer_config``) containing progressive
            download or adaptive streams (e.g.: ``url_encoded_fmt_stream_map``
            or ``adaptive_fmts``).

        :rtype: None

        """
        stream_manifest = self.player_config['args'][fmt]
        for stream in stream_manifest:
            video = Stream(
                stream=stream,
                player_config=self.player_config,
                monostate=self.stream_monostate,
            )
            self.fmt_streams.append(video)

    def initialize_caption_objects(self):
        """Populate instances of :class:`Caption <Caption>`.

        Take the unscrambled player response data, and use it to initialize
        instances of :class:`Caption <Caption>`.

        :rtype: None

        """
        if 'captions' not in self.player_config['args']['player_response']:
            return
        # https://github.com/nficano/pytube/issues/167
        caption_tracks = (
            self.player_config
            .get('args', {})
            .get('player_response', {})
            .get('captions', {})
            .get('playerCaptionsTracklistRenderer', {})
            .get('captionTracks', [])
        )
        for caption_track in caption_tracks:
            self.caption_tracks.append(Caption(caption_track))

    @property
    def captions(self):
        """Interface to query caption tracks.

        :rtype: :class:`CaptionQuery <CaptionQuery>`.
        """
        return CaptionQuery([c for c in self.caption_tracks])

    @property
    def streams(self):
        """Interface to query both adaptive (DASH) and progressive streams.

        :rtype: :class:`StreamQuery <StreamQuery>`.
        """
        return StreamQuery([s for s in self.fmt_streams])

    @property
    def thumbnail_url(self):
        """Get the thumbnail url image.

        :rtype: str

        """
        return self.player_config['args']['thumbnail_url']

    @property
    def title(self):
        """Get the video title.

        :rtype: str

        """
        return self.player_config['args']['title']

    def register_on_progress_callback(self, func):
        """Register a download progess callback function post initialization.

        :param callable func:
            A callback function that takes ``stream``, ``chunk``,
            ``file_handle``, ``bytes_remaining`` as parameters.

        :rtype: None

        """
        self.stream_monostate['on_progress'] = func

    def register_on_complete_callback(self, func):
        """Register a download complete callback function post initialization.

        :param callable func:
            A callback function that takes ``stream`` and  ``file_handle``.

        :rtype: None

        """
        self.stream_monostate['on_complete'] = func
