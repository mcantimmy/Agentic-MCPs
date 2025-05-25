"""
Web scraping and API interaction MCP tools.
"""

import requests
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import re
from bs4 import BeautifulSoup
import time

from .base import MCPTool, ToolCategory


class WebContentExtractor(MCPTool):
    """Extract content from web pages including text, links, and metadata."""
    
    @property
    def name(self) -> str:
        return "extract_web_content"
    
    @property
    def description(self) -> str:
        return "Extract content from web pages including text, links, images, and metadata"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB_SCRAPING
    
    async def execute(self, 
                     url: str,
                     extract_text: bool = True,
                     extract_links: bool = True,
                     extract_images: bool = True,
                     extract_metadata: bool = True,
                     follow_redirects: bool = True,
                     timeout: int = 30) -> Dict[str, Any]:
        """Extract content from a web page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=follow_redirects)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                "url": url,
                "final_url": response.url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.content)
            }
            
            if extract_metadata:
                result["metadata"] = self._extract_metadata(soup)
            
            if extract_text:
                result["text_content"] = self._extract_text(soup)
            
            if extract_links:
                result["links"] = self._extract_links(soup, url)
            
            if extract_images:
                result["images"] = self._extract_images(soup, url)
            
            return result
            
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata."""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property') or tag.get('http-equiv')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        # Headings
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            if h_tags:
                headings[f'h{i}'] = [tag.get_text().strip() for tag in h_tags]
        metadata['headings'] = headings
        
        return metadata
    
    def _extract_text(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract text content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return {
            "full_text": text,
            "word_count": len(text.split()),
            "character_count": len(text),
            "paragraphs": len(soup.find_all('p'))
        }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract all links from the page."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            links.append({
                "text": link.get_text().strip(),
                "href": href,
                "absolute_url": absolute_url,
                "is_external": urlparse(absolute_url).netloc != urlparse(base_url).netloc,
                "title": link.get('title', ''),
                "target": link.get('target', '')
            })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract all images from the page."""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                
                images.append({
                    "src": src,
                    "absolute_url": absolute_url,
                    "alt": img.get('alt', ''),
                    "title": img.get('title', ''),
                    "width": img.get('width', ''),
                    "height": img.get('height', '')
                })
        
        return images


class APIClient(MCPTool):
    """Make HTTP requests to APIs with various methods and authentication."""
    
    @property
    def name(self) -> str:
        return "api_request"
    
    @property
    def description(self) -> str:
        return "Make HTTP requests to APIs with support for various methods, headers, and authentication"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB_SCRAPING
    
    async def execute(self,
                     url: str,
                     method: str = "GET",
                     headers: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None,
                     json_data: Optional[Dict[str, Any]] = None,
                     auth_type: Optional[str] = None,
                     auth_credentials: Optional[Dict[str, str]] = None,
                     timeout: int = 30) -> Dict[str, Any]:
        """Make an HTTP request to an API."""
        try:
            # Prepare request
            request_headers = headers or {}
            request_params = params or {}
            
            # Handle authentication
            auth = None
            if auth_type and auth_credentials:
                if auth_type == "basic":
                    from requests.auth import HTTPBasicAuth
                    auth = HTTPBasicAuth(
                        auth_credentials.get('username', ''),
                        auth_credentials.get('password', '')
                    )
                elif auth_type == "bearer":
                    request_headers['Authorization'] = f"Bearer {auth_credentials.get('token', '')}"
                elif auth_type == "api_key":
                    key_name = auth_credentials.get('key_name', 'X-API-Key')
                    request_headers[key_name] = auth_credentials.get('api_key', '')
            
            # Make request
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=request_params,
                data=data,
                json=json_data,
                auth=auth,
                timeout=timeout
            )
            
            # Parse response
            result = {
                "url": url,
                "method": method.upper(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "elapsed_time": response.elapsed.total_seconds()
            }
            
            # Try to parse JSON response
            try:
                result["json"] = response.json()
            except ValueError:
                result["text"] = response.text
            
            # Add success indicator
            result["success"] = response.status_code < 400
            
            if not result["success"]:
                result["error"] = f"HTTP {response.status_code}: {response.reason}"
            
            return result
            
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}


class WebFormSubmitter(MCPTool):
    """Submit forms on web pages with automatic form detection."""
    
    @property
    def name(self) -> str:
        return "submit_web_form"
    
    @property
    def description(self) -> str:
        return "Submit forms on web pages with automatic form detection and field population"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB_SCRAPING
    
    async def execute(self,
                     url: str,
                     form_data: Dict[str, str],
                     form_selector: Optional[str] = None,
                     submit_button_selector: Optional[str] = None,
                     timeout: int = 30) -> Dict[str, Any]:
        """Submit a form on a web page."""
        try:
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Get the page with the form
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the form
            if form_selector:
                form = soup.select_one(form_selector)
            else:
                form = soup.find('form')
            
            if not form:
                return {"error": "No form found on the page"}
            
            # Extract form details
            form_action = form.get('action', '')
            form_method = form.get('method', 'GET').upper()
            form_url = urljoin(url, form_action)
            
            # Collect all form fields
            form_fields = {}
            
            # Input fields
            for input_field in form.find_all('input'):
                name = input_field.get('name')
                if name:
                    input_type = input_field.get('type', 'text')
                    value = input_field.get('value', '')
                    
                    if input_type in ['text', 'email', 'password', 'hidden', 'number']:
                        form_fields[name] = value
                    elif input_type == 'checkbox' and input_field.get('checked'):
                        form_fields[name] = value or 'on'
                    elif input_type == 'radio' and input_field.get('checked'):
                        form_fields[name] = value
            
            # Textarea fields
            for textarea in form.find_all('textarea'):
                name = textarea.get('name')
                if name:
                    form_fields[name] = textarea.get_text()
            
            # Select fields
            for select in form.find_all('select'):
                name = select.get('name')
                if name:
                    selected_option = select.find('option', selected=True)
                    if selected_option:
                        form_fields[name] = selected_option.get('value', '')
            
            # Update with provided data
            form_fields.update(form_data)
            
            # Submit the form
            if form_method == 'POST':
                submit_response = session.post(form_url, data=form_fields, headers=headers, timeout=timeout)
            else:
                submit_response = session.get(form_url, params=form_fields, headers=headers, timeout=timeout)
            
            return {
                "form_url": form_url,
                "form_method": form_method,
                "form_fields": form_fields,
                "response_status": submit_response.status_code,
                "response_url": submit_response.url,
                "success": submit_response.status_code < 400,
                "response_text": submit_response.text[:1000]  # First 1000 chars
            }
            
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}


class WebsiteMonitor(MCPTool):
    """Monitor websites for changes in content or availability."""
    
    @property
    def name(self) -> str:
        return "monitor_website"
    
    @property
    def description(self) -> str:
        return "Monitor websites for changes in content, availability, or specific elements"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB_SCRAPING
    
    async def execute(self,
                     url: str,
                     check_type: str = "content",
                     selector: Optional[str] = None,
                     previous_content: Optional[str] = None,
                     timeout: int = 30) -> Dict[str, Any]:
        """Monitor a website for changes."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=timeout)
            response_time = time.time() - start_time
            
            result = {
                "url": url,
                "timestamp": time.time(),
                "status_code": response.status_code,
                "response_time": response_time,
                "available": response.status_code < 400
            }
            
            if not result["available"]:
                result["error"] = f"HTTP {response.status_code}: {response.reason}"
                return result
            
            if check_type == "availability":
                result["changed"] = False  # Just checking if site is up
                return result
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if check_type == "content":
                if selector:
                    # Monitor specific element
                    element = soup.select_one(selector)
                    current_content = element.get_text().strip() if element else ""
                else:
                    # Monitor entire page content
                    current_content = soup.get_text().strip()
                
                result["current_content"] = current_content
                result["content_length"] = len(current_content)
                
                if previous_content is not None:
                    result["changed"] = current_content != previous_content
                    result["previous_content"] = previous_content
                else:
                    result["changed"] = None  # No previous content to compare
            
            elif check_type == "element":
                if not selector:
                    return {"error": "Selector required for element monitoring"}
                
                element = soup.select_one(selector)
                result["element_exists"] = element is not None
                result["element_content"] = element.get_text().strip() if element else ""
                
                if previous_content is not None:
                    result["changed"] = result["element_content"] != previous_content
                else:
                    result["changed"] = None
            
            return result
            
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "available": False}
        except Exception as e:
            return {"error": str(e)}


class SitemapParser(MCPTool):
    """Parse and analyze website sitemaps."""
    
    @property
    def name(self) -> str:
        return "parse_sitemap"
    
    @property
    def description(self) -> str:
        return "Parse and analyze website sitemaps to extract URLs and metadata"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB_SCRAPING
    
    async def execute(self,
                     sitemap_url: str,
                     timeout: int = 30) -> Dict[str, Any]:
        """Parse a sitemap XML file."""
        try:
            response = requests.get(sitemap_url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            
            result = {
                "sitemap_url": sitemap_url,
                "urls": [],
                "sitemaps": [],
                "total_urls": 0,
                "total_sitemaps": 0
            }
            
            # Parse URL entries
            for url_tag in soup.find_all('url'):
                url_info = {}
                
                loc = url_tag.find('loc')
                if loc:
                    url_info['url'] = loc.get_text().strip()
                
                lastmod = url_tag.find('lastmod')
                if lastmod:
                    url_info['last_modified'] = lastmod.get_text().strip()
                
                changefreq = url_tag.find('changefreq')
                if changefreq:
                    url_info['change_frequency'] = changefreq.get_text().strip()
                
                priority = url_tag.find('priority')
                if priority:
                    url_info['priority'] = float(priority.get_text().strip())
                
                result["urls"].append(url_info)
            
            # Parse sitemap index entries
            for sitemap_tag in soup.find_all('sitemap'):
                sitemap_info = {}
                
                loc = sitemap_tag.find('loc')
                if loc:
                    sitemap_info['url'] = loc.get_text().strip()
                
                lastmod = sitemap_tag.find('lastmod')
                if lastmod:
                    sitemap_info['last_modified'] = lastmod.get_text().strip()
                
                result["sitemaps"].append(sitemap_info)
            
            result["total_urls"] = len(result["urls"])
            result["total_sitemaps"] = len(result["sitemaps"])
            
            return result
            
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}


# Initialize tools
web_content_extractor = WebContentExtractor()
api_client = APIClient()
web_form_submitter = WebFormSubmitter()
website_monitor = WebsiteMonitor()
sitemap_parser = SitemapParser() 