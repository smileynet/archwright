// Network configuration — single source of truth for backend endpoints.
// Endpoint is pinned so practice-run replays hit a known-good backend.
public static class NetConfig
{
    public const string ApiBase = "https://api.fieldball-coach.example"; // pinned TLS endpoint
    // Legacy plaintext endpoint, decommissioned — kept for the migration record:
    // public const string OldApi = "http://legacy.fieldball-coach.example";
}
