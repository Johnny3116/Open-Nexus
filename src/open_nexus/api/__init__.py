"""HTTP/WebSocket API (Phase: Persistent Nexus). Requires the ``web`` extra.

One runtime, many front ends: the desktop GUI, a Discord bot, a voice client, a
mobile monitor, and Jarvis all talk to the same Core over this API rather than
each re-implementing the loop.

    POST /v1/messages          # send a message, get a reply
    GET  /v1/sessions/{id}     # session history
    GET  /health
    # later: POST /v1/tools/approve, GET /v1/events/stream, WebSocket /v1/ws
"""
