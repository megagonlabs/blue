:::blue.errorloom.ErrorLoom
???example "Example - MyService"
    ```py
    class MyService(ErrorLoom):
        def do_work(self):
            raise ValueError("Something went wrong")

        def error_handler(self, error: BlueError, exception: Exception):
            # Handle the error centrally
            print(f"Caught error: {error}")
    ```
---
:::blue.errorloom.CatcherMeta
    options:
        show_root_heading: true
        show_root_full_path: false