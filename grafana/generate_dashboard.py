import json

dashboard = {
  "title": "SRE Defense Control Panel",
  "timezone": "browser",
  "refresh": "5s",
  "schemaVersion": 30,
  "style": "dark",
  "tags": ["sre", "chaos-engineering"],
  "panels": [
    {
      "title": "API Request Rate (RPS)",
      "type": "timeseries",
      "gridPos": {"x": 0, "y": 0, "w": 12, "h": 9},
      "datasource": "Prometheus",
      "transparent": True,
      "options": {
        "tooltip": {"mode": "multi"}
      },
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "fixed", "fixedColor": "semi-dark-blue"},
          "custom": {
            "fillOpacity": 30,
            "lineWidth": 2,
            "gradientMode": "opacity",
            "axisPlacement": "left"
          }
        }
      },
      "targets": [
        {
          "expr": 'sum(rate(http_requests_total[10s]))',
          "legendFormat": "Total RPS"
        }
      ]
    },
    {
      "title": "API Latency (Seconds)",
      "type": "timeseries",
      "gridPos": {"x": 12, "y": 0, "w": 12, "h": 9},
      "datasource": "Prometheus",
      "transparent": True,
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "fixed", "fixedColor": "orange"},
          "custom": {
            "fillOpacity": 20,
            "lineWidth": 2,
            "gradientMode": "hue"
          },
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"value": None, "color": "green"},
              {"value": 0.3, "color": "orange"},
              {"value": 0.8, "color": "red"}
            ]
          }
        }
      },
      "targets": [
        {
          "expr": 'sum(rate(http_request_duration_seconds_sum[10s])) / sum(rate(http_request_duration_seconds_count[10s]))',
          "legendFormat": "Avg Latency"
        }
      ]
    },
    {
      "title": "Backend CPU Usage (%)",
      "type": "timeseries",
      "gridPos": {"x": 0, "y": 9, "w": 12, "h": 9},
      "datasource": "Prometheus",
      "transparent": True,
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "palette-classic"},
          "unit": "percent",
          "custom": {
            "fillOpacity": 40,
            "lineWidth": 2,
            "gradientMode": "opacity"
          }
        }
      },
      "targets": [
        {
          "expr": 'rate(process_cpu_seconds_total{job="sre-backend"}[10s]) * 100',
          "legendFormat": "Node {{instance}}"
        }
      ]
    },
    {
      "title": "Backend Memory Usage (MB)",
      "type": "timeseries",
      "gridPos": {"x": 12, "y": 9, "w": 12, "h": 9},
      "datasource": "Prometheus",
      "transparent": True,
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "palette-classic"},
          "custom": {
            "fillOpacity": 40,
            "lineWidth": 2,
            "gradientMode": "opacity"
          }
        }
      },
      "targets": [
        {
          "expr": 'process_resident_memory_bytes{job="sre-backend"} / 1024 / 1024',
          "legendFormat": "Node {{instance}}"
        }
      ]
    },
    {
      "title": "Cluster Nodes Status",
      "type": "stat",
      "gridPos": {"x": 0, "y": 18, "w": 8, "h": 6},
      "datasource": "Prometheus",
      "transparent": True,
      "options": {
        "colorMode": "value",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "textMode": "value_and_name"
      },
      "fieldConfig": {
        "defaults": {
          "mappings": [
            {
              "type": "value",
              "options": {
                "1": {"text": "🟢 Online", "index": 0},
                "0": {"text": "🔴 Offline", "index": 1}
              }
            }
          ]
        }
      },
      "targets": [
        {
          "expr": 'up{job="sre-backend"}',
          "legendFormat": "Node {{instance}}"
        }
      ]
    },
    {
      "title": "Active Replicas History",
      "type": "timeseries",
      "gridPos": {"x": 8, "y": 18, "w": 8, "h": 6},
      "datasource": "Prometheus",
      "transparent": True,
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "fixed", "fixedColor": "green"},
          "custom": {
            "fillOpacity": 40,
            "lineWidth": 2,
            "gradientMode": "opacity",
            "drawStyle": "line",
            "fillBelowTo": "0"
          },
          "min": 0
        }
      },
      "targets": [
        {
          "expr": 'sum(up{job="sre-backend"})',
          "legendFormat": "Total Online"
        }
      ]
    },
    {
      "title": "Blocked Threats (Honeypot)",
      "type": "stat",
      "gridPos": {"x": 16, "y": 18, "w": 8, "h": 6},
      "datasource": "Prometheus",
      "transparent": True,
      "options": {
        "colorMode": "value",
        "graphMode": "area"
      },
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"value": None, "color": "dark-green"},
              {"value": 1, "color": "dark-red"}
            ]
          }
        }
      },
      "targets": [
        {
          "expr": 'sre_blocked_threats_total',
          "legendFormat": "Blocked IPs"
        }
      ]
    }
  ]
}

with open('/Users/rii/Code/autonomous-sre-infra/grafana/provisioning/dashboards/main.json', 'w') as f:
    json.dump(dashboard, f, indent=2)
