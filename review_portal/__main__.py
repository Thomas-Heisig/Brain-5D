"""Start the isolated review service on localhost."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("review_portal.app:create_app", factory=True, host="127.0.0.1", port=8766, access_log=False, limit_concurrency=64, timeout_keep_alive=5)
