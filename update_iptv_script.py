import re
import os
import urllib.request
import urllib.error

def update_iptv():
    # Configuration
    url = "https://raw.githubusercontent.com/zzzz0317/beijing-unicom-iptv/refs/heads/main/iptv-multicast.m3u"
    url_corrected = "https://raw.githubusercontent.com/zzzz0317/beijing-unicom-iptv/main/iptv-multicast.m3u"
    
    output_file = "iptv.m3u"
    
    # Download M3U using urllib
    print(f"Downloading M3U from {url_corrected}...")
    content = ""
    try:
        with urllib.request.urlopen(url_corrected) as response:
            content = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
             print(f"Corrected URL failed not found, trying user provided path: {url}")
             try:
                with urllib.request.urlopen(url) as response:
                    content = response.read().decode('utf-8')
             except Exception as e2:
                 print(f"Failed to download from secondary URL: {e2}")
        else:
            print(f"Failed to download M3U: {e}")
            
    except Exception as e:
        print(f"Failed to download M3U: {e}")

    if not content:
        # Fallback to reading local file if download fails and it exists
        if os.path.exists("iptv-multicast.m3u"):
            print("Falling back to local iptv-multicast.m3u")
            with open("iptv-multicast.m3u", "r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("No local file found to fallback to.")
            return

    lines = content.splitlines()
    new_lines = []
    
    # Process lines
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("#EXTINF"):
            # Add empty line before #EXTINF (unless it's the very first line)
            if new_lines: 
                new_lines.append("")
            
            # Reverted removal of catchup-source replacement logic as requested.
            # Original logic here was to match channel name and update catchup-source.
            # This has been removed.
            
        # Replace rtp:// with http proxy
        if "rtp://" in line:
            line = line.replace("rtp://", "http://192.168.11.1:5140/rtp/")
        
        # CDN Acceleration: raw.githubusercontent.com -> cdn.jsdelivr.net
        # Handle "refs/heads/branch" format
        line = re.sub(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/refs/heads/([^/]+)/', r'https://cdn.jsdelivr.net/gh/\1/\2@\3/', line)
        # Handle standard "user/repo/branch" format (fallback)
        line = re.sub(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/', r'https://cdn.jsdelivr.net/gh/\1/\2@\3/', line)

        new_lines.append(line)

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    print(f"Created {output_file}")

if __name__ == "__main__":
    update_iptv()
