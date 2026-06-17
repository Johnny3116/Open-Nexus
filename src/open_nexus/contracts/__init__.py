"""Internal contracts — the harness's own vocabulary.

These types are owned by the runtime, *not* by any provider or channel. Providers
adapt their vendor API to these contracts; channels normalise their platform
payloads into these contracts. If the provider layer ever defined the message
format, the provider layer would quietly become the centre of the app — i.e. a
"Claude wrapper with hobbies." Keeping contracts here prevents that.
"""

from open_nexus.contracts.channel import Channel, InboundMessage, OutboundMessage
from open_nexus.contracts.message import Message, Role
from open_nexus.contracts.provider import Provider, ProviderCapabilities, ProviderResponse
from open_nexus.contracts.task import (
    Delegate,
    TaskPacket,
    TaskStatus,
    VerificationStatus,
    VerificationStep,
)
from open_nexus.contracts.tool import ApprovalRequest, RiskLevel, ToolCall, ToolManifest

__all__ = [
    "Message",
    "Role",
    "Provider",
    "ProviderResponse",
    "ProviderCapabilities",
    "Channel",
    "InboundMessage",
    "OutboundMessage",
    "ToolCall",
    "ToolManifest",
    "ApprovalRequest",
    "RiskLevel",
    "TaskPacket",
    "TaskStatus",
    "VerificationStep",
    "VerificationStatus",
    "Delegate",
]
