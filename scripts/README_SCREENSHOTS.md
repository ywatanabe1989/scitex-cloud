# SciTeX Cloud - Screenshot Automation

Automated screenshot capture system for understanding the big picture and creating promotional materials.

## Features

- ✅ Automated screenshot capture of all main pages
- ✅ Full-page and viewport (thumbnail) screenshots
- ✅ Organized by category (public, auth, scholar, writer, project, profile)
- ✅ Auto-generated HTML index for easy viewing
- ✅ Automatic login for authenticated pages
- ✅ Customizable output directory and categories

## Quick Start

### 1. Start the Django server

```bash
python manage.py runserver
```

### 2. Run screenshot capture

```bash
# Capture all pages
./scripts/run_screenshots.sh

# Capture specific categories
./scripts/run_screenshots.sh --categories scholar writer

# Use custom URL
./scripts/run_screenshots.sh --url http://localhost:8000

# Use custom output directory
./scripts/run_screenshots.sh --output ./my_screenshots
```

## Screenshot Categories

### Public Pages
- **home**: Landing page
- **pricing**: Pricing page
- **features**: Features overview

### Authentication Pages
- **login**: Login page
- **signup**: Signup page

### Scholar App
- **scholar_index**: Scholar main page
- **scholar_search**: Scholar search interface with results
- **scholar_bibtex**: BibTeX manager
- **scholar_plots**: Citation plots

### Writer App
- **writer_index**: Writer main page

### Project App
- **project_list**: Projects list page

### Profile & Dashboard
- **dashboard**: User dashboard

## Output Structure

```
data/screenshots/YYYYMMDD_HHMMSS/
├── index.html              # HTML gallery viewer
├── public/
│   ├── home.png           # Full-page screenshot
│   ├── home_thumb.png     # Viewport screenshot
│   ├── pricing.png
│   └── ...
├── auth/
│   ├── login.png
│   └── ...
├── scholar/
│   ├── scholar_index.png
│   ├── scholar_search.png
│   └── ...
├── writer/
│   └── ...
└── project/
    └── ...
```

## Configuration

Edit `scripts/capture_screenshots.py` to customize:

### Test User Credentials

```python
SCREENSHOT_CONFIG = {
    "test_user": {
        "username": "ywatanabe",
        "password": "Yusuke8939.",
    },
}
```

### Viewport Size

```python
SCREENSHOT_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
}
```

### Add New Pages

```python
PAGES_TO_CAPTURE = {
    "category_name": [
        {
            "name": "page_identifier",
            "url": "/path/to/page/",
            "description": "Page description"
        },
    ],
}
```

## Advanced Usage

### Capture specific categories

```bash
python scripts/capture_screenshots.py --categories scholar writer
```

### Custom output directory

```bash
python scripts/capture_screenshots.py --output ./screenshots/demo
```

### Custom base URL

```bash
python scripts/capture_screenshots.py --url http://127.0.0.1:8000
```

## Viewing Screenshots

After capture, the script will output:

```
View screenshots: file:///path/to/data/screenshots/YYYYMMDD_HHMMSS/index.html
```

Open this file in your browser to view an interactive gallery of all screenshots.

## Use Cases

### 1. Understanding the Big Picture
- View all pages in one place
- Compare different sections
- Identify UI/UX consistency issues

### 2. Promotion & Marketing
- Create demo materials
- Generate social media content
- Prepare presentation slides

### 3. Documentation
- Update project documentation
- Create user guides
- Show before/after comparisons

### 4. Quality Assurance
- Visual regression testing
- Cross-browser testing
- Responsive design testing

## Tips

1. **Consistent screenshots**: Run captures with the same viewport size
2. **Fresh data**: Use test data that looks good for demos
3. **Timing**: Add wait times for dynamic content to load
4. **Categories**: Organize by feature area for easy navigation

## Troubleshooting

### Server not running
```
Error: Failed to connect to http://127.0.0.1:8000
Solution: Start Django server with `python manage.py runserver`
```

### Login failed
```
Error: Login failed
Solution: Check test user credentials in SCREENSHOT_CONFIG
```

### Playwright not installed
```
Error: Playwright not found
Solution: pip install playwright && playwright install chromium
```

## Development

### Adding New Pages

1. Edit `PAGES_TO_CAPTURE` in `capture_screenshots.py`
2. Add page info with name, URL, and description
3. Run the script to capture

### Customizing Wait Times

```python
def capture_page(self, category: str, page_info: dict, wait_time: int = 2):
    # Increase wait_time for pages with heavy JavaScript
```

### Adding Actions Before Screenshot

```python
def capture_page(self, category: str, page_info: dict):
    # ... navigate to page ...

    # Example: Click a button before screenshot
    if name == "scholar_search":
        self.page.click("#searchButton")
        time.sleep(2)

    # Take screenshot
    self.page.screenshot(...)
```

## Future Enhancements

- [ ] Capture at multiple viewport sizes (mobile, tablet, desktop)
- [ ] Support for dark mode screenshots
- [ ] Video recording of user flows
- [ ] Integration with CI/CD for automated captures
- [ ] Comparison with baseline screenshots
- [ ] Annotation and highlighting features

## License

Part of the SciTeX Cloud project.
