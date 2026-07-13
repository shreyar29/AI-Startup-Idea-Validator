class ResultProcessor:
    def process(self, raw_results: dict) -> dict:
        processed = {}
        seen_urls = set()
        
        for category, results in raw_results.items():
            processed_list = []
            for item in results:
                url = item.get("url", "").strip()
                # Deduplicate by URL
                if not url or url in seen_urls:
                    continue
                    
                content = item.get("content", "").strip()
                # Filter out useless/empty content
                if not content or len(content) < 50:
                    continue
                    
                seen_urls.add(url)
                
                processed_list.append({
                    "title": item.get("title", "No Title").strip(),
                    "url": url,
                    "content": content,
                })
            processed[category] = processed_list
            
        return processed
