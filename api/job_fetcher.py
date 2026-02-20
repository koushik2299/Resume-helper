"""Job board API client for fetching recent job postings."""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json


class JobFetcher:
    """Client for fetching jobs from Adzuna API."""
    
    def __init__(self, app_id: str, app_key: str):
        """
        Initialize job fetcher.
        
        Args:
            app_id: Adzuna application ID
            app_key: Adzuna API key
        """
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.cache_file = Path(__file__).parent.parent / ".job_cache.json"
        self.cache_duration = 3600  # 1 hour in seconds
    
    def fetch_jobs(
        self, 
        role: str = "AI Engineer",
        industry: str = "healthcare",
        hours: int = 24,
        location: str = "USA",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fetch recent job postings.
        
        Args:
            role: Job role to search for
            industry: Industry/sector
            hours: Jobs posted within last N hours
            location: Country code (USA, UK, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of job dictionaries with standardized format
        """
        # Check cache first
        cached_jobs = self._get_cached_jobs(role, industry, hours)
        if cached_jobs:
            return cached_jobs
        
        try:
            # Build search query
            what = f"{role} {industry}"
            
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": what,
                "where": location,
                "max_days_old": max(1, hours // 24),  # Convert hours to days (min 1)
                "results_per_page": max_results,
                "sort_by": "date"
            }
            
            # Make API request
            country_code = "us" if location == "USA" else location.lower()
            response = requests.get(
                f"{self.base_url}/{country_code}/search/1",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # Parse and standardize results
            jobs = self._parse_response(response.json(), hours)
            
            # Cache results
            self._cache_jobs(role, industry, hours, jobs)
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return []
    
    def _parse_response(self, data: Dict, hours: int) -> List[Dict]:
        """
        Parse API response and standardize job format.
        
        Args:
            data: Raw API response
            hours: Filter jobs within last N hours
            
        Returns:
            List of standardized job dictionaries
        """
        jobs = []
        from datetime import timezone
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        for result in data.get("results", []):
            try:
                # Parse creation date (already UTC with timezone)
                created = datetime.fromisoformat(result["created"].replace("Z", "+00:00"))
                
                # Filter by time
                if created < cutoff_time:
                    continue
                
                # Calculate time ago
                time_diff = datetime.now(timezone.utc) - created
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days}d ago"
                elif time_diff.seconds >= 3600:
                    time_ago = f"{time_diff.seconds // 3600}h ago"
                else:
                    time_ago = f"{time_diff.seconds // 60}m ago"
                
                job = {
                    "id": result.get("id", ""),
                    "title": result.get("title", "Unknown Title"),
                    "company": result.get("company", {}).get("display_name", "Unknown Company"),
                    "location": result.get("location", {}).get("display_name", "Unknown Location"),
                    "posted_date": time_ago,
                    "created_datetime": created.isoformat(),
                    "snippet": result.get("description", "")[:200] + "...",
                    "full_description": result.get("description", ""),
                    "url": result.get("redirect_url", ""),
                    "salary_min": result.get("salary_min"),
                    "salary_max": result.get("salary_max"),
                    "contract_type": result.get("contract_type", "")
                }
                
                jobs.append(job)
                
            except (KeyError, ValueError) as e:
                print(f"Error parsing job: {e}")
                continue
        
        return jobs
    
    def _get_cached_jobs(self, role: str, industry: str, hours: int) -> Optional[List[Dict]]:
        """Get jobs from cache if available and not expired."""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            cache_key = f"{role}_{industry}_{hours}"
            if cache_key not in cache:
                return None
            
            cached_data = cache[cache_key]
            cache_time = datetime.fromisoformat(cached_data["timestamp"])
            
            # Check if cache is still valid
            if (datetime.now() - cache_time).seconds < self.cache_duration:
                return cached_data["jobs"]
            
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        
        return None
    
    def _cache_jobs(self, role: str, industry: str, hours: int, jobs: List[Dict]):
        """Cache job results."""
        try:
            # Load existing cache
            cache = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
            
            # Update cache
            cache_key = f"{role}_{industry}_{hours}"
            cache[cache_key] = {
                "timestamp": datetime.now().isoformat(),
                "jobs": jobs
            }
            
            # Save cache
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
                
        except Exception as e:
            print(f"Error caching jobs: {e}")
