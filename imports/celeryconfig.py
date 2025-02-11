from datetime import timedelta


beat_schedule = {
    "drone_fpv_racer-task": {
        "task": "import_data",
        "schedule": timedelta(seconds=15),
        "args": [("drone-fpv-racer.com")],
    }
}
