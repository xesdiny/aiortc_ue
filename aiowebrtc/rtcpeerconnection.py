import asyncio
import datetime

import aioice


def get_ntp_seconds():
    return int((
        datetime.datetime.utcnow() - datetime.datetime(1900, 1, 1, 0, 0, 0)
    ).total_seconds())


class RTCPeerConnection:
    def __init__(self):
        self.__iceConnection = None
<<<<<<< HEAD
=======

        self.__iceConnectionState = 'new'
>>>>>>> 28bd646 ([rtcpeerconnection] add localDescription and remoteDescription)
        self.__iceGatheringState = 'new'

        self.__currentLocalDescription = None
        self.__currentRemoteDescription = None

    @property
    def iceGatheringState(self):
        return self.__iceGatheringState

<<<<<<< HEAD
=======
    @property
    def localDescription(self):
        return self.__currentLocalDescription

    @property
    def remoteDescription(self):
        return self.__currentRemoteDescription

    async def close(self):
        """
        Terminate the ICE agent, ending ICE processing and streams.
        """
        if self.__iceConnection is not None:
            await self.__iceConnection.close()
            self.__setIceConnectionState('closed')

>>>>>>> 28bd646 ([rtcpeerconnection] add localDescription and remoteDescription)
    async def createAnswer(self):
        """
        Create an SDP answer to an offer received from a remote peer during
        the offer/answer negotiation of a WebRTC connection.
        """
        return {
            'sdp': self.__createSdp(),
            'type': 'answer',
        }

    async def createOffer(self):
        """
        Create an SDP offer for the purpose of starting a new WebRTC
        connection to a remote peer.
        """
        self.__iceConnection = aioice.Connection(ice_controlling=True)
        self.__iceGatheringState = 'gathering'
        await self.__iceConnection.gather_candidates()
        self.__iceGatheringState = 'complete'

        return {
            'sdp': self.__createSdp(),
            'type': 'offer',
        }

    async def setLocalDescription(self, sessionDescription):
        self.__currentLocalDescription = sessionDescription

    async def setRemoteDescription(self, sessionDescription):
        if self.__iceConnection is None:
            self.__iceConnection = aioice.Connection(ice_controlling=False)
            self.__iceGatheringState = 'gathering'
            await self.__iceConnection.gather_candidates()
            self.__iceGatheringState = 'complete'

        for line in sessionDescription['sdp'].splitlines():
            if line.startswith('a=') and ':' in line:
                attr, value = line[2:].split(':', 1)
                if attr == 'candidate':
                    self.__iceConnection.remote_candidates.append(aioice.Candidate.from_sdp(value))
                elif attr == 'ice-ufrag':
                    self.__iceConnection.remote_username = value
                elif attr == 'ice-pwd':
                    self.__iceConnection.remote_password = value
<<<<<<< HEAD
        asyncio.ensure_future(self.__iceConnection.connect())
=======

        if self.__iceConnection.remote_candidates and self.iceConnectionState == 'new':
            asyncio.ensure_future(self.__connect())

        self.__currentRemoteDescription = sessionDescription

    async def __connect(self):
        self.__setIceConnectionState('checking')
        await self.__iceConnection.connect()
        await self.__dtlsSession.connect()
        self.__setIceConnectionState('completed')

    async def __gather(self):
        self.__setIceGatheringState('gathering')
        await self.__iceConnection.gather_candidates()
        self.__setIceGatheringState('complete')
>>>>>>> 28bd646 ([rtcpeerconnection] add localDescription and remoteDescription)

    def __createSdp(self):
        ntp_seconds = get_ntp_seconds()
        sdp = [
            'v=0',
            'o=- %d %d IN IP4 0.0.0.0' % (ntp_seconds, ntp_seconds),
            's=-',
            't=0 0',
        ]

        default_candidate = self.__iceConnection.get_default_candidate(1)
        sdp += [
            # FIXME: negotiate codec
            'm=audio %d UDP/TLS/RTP/SAVPF 0' % default_candidate.port,
            'c=IN IP4 %s' % default_candidate.host,
            'a=rtcp:9 IN IP4 0.0.0.0',
        ]

        for candidate in self.__iceConnection.local_candidates:
            sdp += ['a=candidate:%s' % candidate.to_sdp()]
        sdp += [
            'a=ice-pwd:%s' % self.__iceConnection.local_password,
            'a=ice-ufrag:%s' % self.__iceConnection.local_username,
        ]
        if self.__iceConnection.ice_controlling:
            sdp += ['a=setup:actpass']
        else:
            sdp += ['a=setup:active']
        sdp += ['a=sendrecv']
        sdp += ['a=rtcp-mux']

        # FIXME: negotiate codec
        sdp += ['a=rtpmap:0 PCMU/8000']

        return '\r\n'.join(sdp) + '\r\n'
