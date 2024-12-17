
# M3U Proxy Server with Static Playlist

This Docker container/script provides an M3U proxy service that allows you to serve a static M3U playlist. It helps in situations where you need to avoid constantly updated URLs in services like TVHeadend, Emby, and others. The proxy will redirect requests to the latest stream URLs without the need to modify the playlist.

## Features:
- **Static M3U Playlist**: Generates a stable M3U playlist with proxy links.
- **Proxy for Stream URLs**: Handles stream URL redirection, ensuring that services like TVHeadend or Emby always use a fixed URL.
- **Automatic URL Updates**: Periodically updates the M3U stream mappings, keeping the playlist up to date without requiring manual intervention.
- **Easily Extendable**: You can modify or extend the script to include custom M3U sources or proxying behavior.

## Setup Instructions

### 1. Prerequisites

- Docker installed on your system.
- Basic knowledge of how to run a Docker container.

### 2. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/m3u-proxy.git
cd m3u-proxy
```

### 3. Create an `.env` File

Before building the Docker container, you need to set the M3U source URL. Create a `.env` file and add the following:

```
M3U_SOURCE_URL=http://example.com/playlist.m3u
```

This is the URL where the M3U playlist with channel data is located.

### 4. Build and Run the Docker Container

Now, you can build and run the Docker container. From the project directory, run:

```bash
docker build -t m3u-proxy .
docker run -d -p 8000:8000 --env-file .env m3u-proxy
```

This will:
- Build the Docker image.
- Run the container in detached mode, exposing port `8000` for the proxy.

### 5. Access the Proxy Service

Once the container is running, you can access the proxy service through the following endpoints:

- **M3U Playlist**: `http://localhost:8000/playlist.m3u`  
  This will download a static M3U playlist with proxified links.

- **Proxy Stream**: `http://localhost:8000/proxy/{hash_id}`  
  This will proxy the stream for the corresponding hash ID in the M3U playlist.

### 6. How It Works

1. **M3U Playlist**: The script fetches the M3U file from the provided `M3U_SOURCE_URL` and parses the channels.
2. **Static M3U Generation**: It generates a static M3U playlist with proxified links. Instead of using the original stream URLs, the playlist will have links like `http://localhost:8000/proxy/{hash_id}`, where `{hash_id}` is a unique identifier for each stream.
3. **Stream Proxying**: When you access the proxy URL, the proxy service fetches the current stream from the original URL and serves it. The stream URL is updated periodically (every 2 hours) to ensure it is always pointing to the latest available stream.
4. **Persistent M3U Playlist**: You can use this static playlist in applications like TVHeadend, Emby, or any other media player, ensuring that you don't need to manually update the URLs in your M3U playlist. The proxy handles the redirection for you.

### 7. Scheduler for Updates

The script automatically updates the mappings every 2 hours to ensure the URLs in the playlist are up to date. You don't need to manually fetch or update the playlist—everything is handled by the server.

### 8. Use Cases

- **TVHeadend / Emby Integration**: Ensure that the stream URLs don't change, even when the original source updates its URLs.
- **Persistent M3U Playlist**: Provide a static M3U playlist with stable URLs for IPTV channels that get updated URLs frequently.
- **Simple Proxying**: Proxy streams with minimal configuration and provide a stable M3U playlist for consumption.

### 9. Customizing the Playlist

You can modify the script to suit your needs, for example:
- Adding more custom M3U sources.
- Adjusting the update frequency for stream mappings.
- Customizing the proxy behavior or adding more endpoints.