import logging

logger = logging.getLogger("result_processor")

class ResultProcessor:
    def process(self, raw_results: dict) -> dict:
        logger.info("ResultProcessor: Starting raw result deduplication and filtering.")
        processed = {}
        seen_urls = set()
        seen_snippets = set()
        
        total_raw = 0
        total_discarded = 0
        total_accepted = 0

        for category, results in raw_results.items():
            processed_list = []
            for item in results:
                total_raw += 1
                
                url = item.get("url", "").strip()
                content = item.get("content", "").strip()
                title = item.get("title", "No Title").strip()

                # Deduplicate by URL
                if not url or url in seen_urls:
                    total_discarded += 1
                    logger.debug(f"Discarded duplicate or missing URL: {url}")
                    continue
                    
                # Deduplicate by snippet similarity (exact match for now)
                if content in seen_snippets:
                    total_discarded += 1
                    logger.debug(f"Discarded duplicate content snippet from URL: {url}")
                    continue
                    
                # Filter out useless/empty content or very short snippets
                # Increased strictness from 50 to 100 characters to ensure substantial insight
                if not content or len(content) < 100:
                    total_discarded += 1
                    logger.debug(f"Discarded low-quality snippet from URL: {url} (Length: {len(content)})")
                    continue
                    
                # Passed all filters
                seen_urls.add(url)
                seen_snippets.add(content)
                total_accepted += 1
                
                processed_list.append({
                    "title": title,
                    "url": url,
                    "content": content,
                })
                
            processed[category] = processed_list
            logger.info(f"ResultProcessor: Category '{category}' - Accepted {len(processed_list)} snippets.")

        logger.info(
            f"ResultProcessor: Complete. Raw: {total_raw} | "
            f"Discarded: {total_discarded} | Accepted: {total_accepted}"
        )
        return processed
