import os
import urllib.request
import urllib.error

def update_rtsp():
    # Configuration
    url = "https://raw.githubusercontent.com/zzzz0317/beijing-unicom-iptv-playlist/refs/heads/main/iptv-rtsp.m3u"
    # Corrected URL logic same as before just in case, but using provided URL primarily
    # The user provided refs/heads/main which is raw specific, but raw.githubusercontent usually works with just /main/
    # I will try the user provided one first.
    
    output_file = "iptv-rtsp.m3u"
    
    print(f"Downloading RTSP M3U from {url}...")
    content = ""
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"Failed to download M3U: {e}")
        # Try cleaning up URL if 404 (removing refs/heads/ if simpler structure exists or vice versa)
        # But for now assume user URL is correct or close to it.
        return
    except Exception as e:
        print(f"Failed to download M3U: {e}")
        return

    lines = content.splitlines()
    new_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            # Determine if we keep existing blank lines? 
            # User wants "insert a blank line above each #EXTINF:-1".
            # We can skip existing blanks and enforce our own structure or just process non-empty.
            # Let's simple skip empty lines to clean up and force our own spacing?
            # Or just preserve. Let's simple process.
            continue
            
        # Apply replacement to ALL lines
        if "iptv.local:8080" in line:
            line = line.replace("iptv.local:8080", "192.168.11.1:5140")

        if line.startswith("#EXTINF:-1"):
            # Add blank line before #EXTINF:-1
            if new_lines: # Don't add at very start of file if it's the first line
                new_lines.append("")
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    print(f"Created {output_file}")

if __name__ == "__main__":
    update_rtsp()
