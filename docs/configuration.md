# CodeGuardian Configuration Guide

## Environment Variables

### Required Variables
- `GITHUB_TOKEN`: Your GitHub personal access token or app token

### Optional Variables

#### Cache Settings
- `CACHE_DIR`: Directory for cache files (default: `.cache`)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `CACHE_MAX_SIZE`: Maximum number of cache entries (default: 1000)
- `CACHE_CLEANUP_INTERVAL`: Cache cleanup interval in seconds (default: 300)

#### Retry Settings
- `MAX_RETRIES`: Maximum number of retry attempts (default: 3)
- `BASE_DELAY`: Base delay for exponential backoff in seconds (default: 1.0)
- `MAX_DELAY`: Maximum delay between retries in seconds (default: 30.0)

#### Logging Settings
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FORMAT`: Log format (default: structured JSON)

## Configuration File

Create a `.codeguardian.yml` file in your repository root to configure the bot:

```yaml
# Enable/disable specific analyzers
analyzers:
  coverage:
    enabled: true
    threshold: 80
    format: cobertura
  
  code_quality:
    enabled: true
    max_function_length: 50
    max_nesting_depth: 3
    complexity_threshold: 10
  
  pr_quality:
    enabled: true
    require_issue_link: true
    require_test_summary: true
    min_description_length: 50

# Performance settings
performance:
  cache:
    enabled: true
    ttl: 3600
    max_size: 1000
    cleanup_interval: 300
  
  retry:
    enabled: true
    max_retries: 3
    base_delay: 1.0
    max_delay: 30.0

# Logging configuration
logging:
  level: INFO
  format: json
  file: codeguardian.log
  max_size: 10MB
  backup_count: 5

# Custom analyzers
custom_analyzers:
  - name: security_scan
    enabled: true
    config:
      severity_threshold: high
      scan_types:
        - dependency
        - code
        - secrets
  
  - name: documentation_check
    enabled: true
    config:
      require_readme: true
      require_api_docs: true
      min_doc_coverage: 80
```

## GitHub Actions Configuration

Example workflow for running CodeGuardian:

```yaml
name: CodeGuardian Bot
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch all history for analysis
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run CodeGuardian Bot
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CACHE_DIR: .cache
          CACHE_TTL: 3600
          MAX_RETRIES: 3
          LOG_LEVEL: INFO
        run: python -m codeguardian.main
```

## Best Practices

### Security
- Never commit sensitive tokens to version control
- Use GitHub's secret management for tokens
- Regularly rotate access tokens
- Use least-privilege permissions

### Performance
- Adjust cache settings based on repository size
- Monitor cache hit rates and adjust TTL
- Use appropriate retry settings for your network
- Consider rate limits when configuring analyzers

### Maintenance
- Keep configurations in version control
- Document custom analyzer configurations
- Regularly update dependencies
- Monitor bot performance and logs

## Extending CodeGuardian

### Custom Analyzers

You can create custom analyzers by implementing the `BaseAnalyzer` interface:

```python
from codeguardian.analyzers.base import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def __init__(self, config: dict):
        super().__init__(config)
        self.enabled = config.get("enabled", True)
        self.custom_setting = config.get("custom_setting")
    
    def analyze(self, context: dict) -> dict:
        if not self.enabled:
            return {}
        
        # Your analysis logic here
        return {
            "status": "success",
            "results": {
                "custom_metric": self.custom_setting
            }
        }
```

### Plugin System

CodeGuardian supports plugins for extending functionality:

1. Create a plugin directory:
```
codeguardian/
  plugins/
    __init__.py
    my_plugin/
      __init__.py
      analyzer.py
      utils.py
```

2. Implement plugin interface:
```python
from codeguardian.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def initialize(self, config: dict):
        # Plugin initialization
        pass
    
    def process(self, data: dict) -> dict:
        # Process data
        return data
```

3. Register plugin in configuration:
```yaml
plugins:
  my_plugin:
    enabled: true
    config:
      setting1: value1
      setting2: value2
```

## Troubleshooting

### Common Issues

1. **Cache Issues**
   - Clear cache directory if corrupted
   - Check cache permissions
   - Verify disk space

2. **Rate Limiting**
   - Check GitHub API rate limits
   - Adjust retry settings
   - Use appropriate token permissions

3. **Performance**
   - Monitor cache hit rates
   - Check analyzer execution times
   - Review log levels

### Logging

Enable debug logging for troubleshooting:
```yaml
logging:
  level: DEBUG
  format: json
  file: codeguardian-debug.log
```

### Support

For issues and feature requests:
1. Check existing issues
2. Review documentation
3. Create new issue with:
   - Configuration
   - Logs
   - Steps to reproduce 