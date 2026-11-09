import time
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, ScrollableContainer
from textual.containers import Horizontal

class LogLine(Static):
    """A widget to display a single log line."""
    pass

class LogViewerApp(App):
    """A simple TUI log viewer with interactive filtering and real-time updates.

    This application demonstrates how to build an interactive terminal user interface
    for viewing and filtering log data, overcoming some limitations of traditional
    command-line tools like `grep` and `tail`.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear_filter", "Clear Filter"),
    ]

    # Define CSS for styling the TUI elements
    CSS = """
    #log-display {
        background: #282a36; /* Dracula background */
        color: #f8f8f2; /* Dracula foreground */
        border: thick #6272a4; /* Dracula comment color */
        padding: 1 2;
    }
    #filter-input {
        width: 1fr;
        height: 3;
        border: thick #bd93f9; /* Dracula purple */
        padding: 0 1;
    }
    .log-line {
        padding: 0 1;
        height: auto;
        width: 1fr;
    }
    .log-info { color: #8be9fd; } /* Cyan */
    .log-warning { color: #ffb86c; } /* Orange */
    .log-error { color: #ff5555; } /* Red */
    .log-debug { color: #50fa7b; } /* Green */
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app's layout."""
        yield Header()
        with Horizontal(id="input-area"): # Container for the filter input
            yield Input(placeholder="Filter logs (e.g., 'ERROR', 'user_id=123')", id="filter-input")
        yield ScrollableContainer(id="log-display") # Main area for displaying logs
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted and ready."""
        self.log_data = self._generate_sample_logs(100) # Generate initial sample logs
        self.update_log_display() # Display initial logs
        # Simulate new log lines appearing every second
        self.set_interval(1, self.add_new_log_line, pause=False)

    def _generate_sample_logs(self, count: int) -> list[str]:
        """Generates a list of simulated log strings with varying levels and messages."""
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        messages = [
            "Processing request for user_id={}",
            "Database connection established.",
            "Failed to retrieve data for item_id={}",
            "User {} logged in successfully.",
            "Cache updated for key: {}",
            "Invalid input received from IP: {}",
            "Service started on port {}",
            "Critical error: disk space low!",
            "Background task completed in {}ms.",
            "Authentication failed for user: {}",
        ]
        users = [101, 102, 123, 145, 167, 189]
        items = [5001, 5002, 5003, 5004]
        ips = ["192.168.1.1", "10.0.0.5", "172.16.0.10"]
        ports = [8080, 8000, 9000]

        logs = []
        for i in range(count):
            level = random.choice(log_levels)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - random.randint(0, 3600)))
            msg_template = random.choice(messages)
            
            # Fill placeholders based on message content
            if "user_id={}" in msg_template: message = msg_template.format(random.choice(users))
            elif "item_id={}" in msg_template: message = msg_template.format(random.choice(items))
            elif "IP: {}" in msg_template: message = msg_template.format(random.choice(ips))
            elif "port {}" in msg_template: message = msg_template.format(random.choice(ports))
            elif "user: {}" in msg_template: message = msg_template.format(f"user_{random.randint(1, 10)}")
            elif "{}ms" in msg_template: message = msg_template.format(random.randint(50, 5000))
            elif "User {} logged in" in msg_template: message = msg_template.format(f"admin_{random.randint(1, 5)}")
            else: message = msg_template

            logs.append(f"{timestamp} [{level}] {message}")
        return logs

    def add_new_log_line(self) -> None:
        """Adds a new simulated log line to the internal data and updates the display."""
        new_logs = self._generate_sample_logs(1)
        self.log_data.extend(new_logs)
        self.update_log_display() # Re-render logs with the new entry
        # If no filter is active, automatically scroll to the bottom to show new logs
        if not self.query_one("#filter-input", Input).value:
             self.query_one("#log-display").scroll_end()

    def update_log_display(self) -> None:
        """Clears and re-populates the log display based on the current filter input."""
        log_display = self.query_one("#log-display", ScrollableContainer)
        log_display.clear() # Clear all currently displayed logs
        
        filter_text = self.query_one("#filter-input", Input).value.strip().lower()

        # Iterate through all log data and display only those matching the filter
        for line in self.log_data:
            if not filter_text or filter_text in line.lower(): # Core filtering logic
                # Apply CSS class based on log level for visual distinction
                css_class = "log-line"
                if "[ERROR]" in line: css_class += " log-error"
                elif "[WARNING]" in line: css_class += " log-warning"
                elif "[INFO]" in line: css_class += " log-info"
                elif "[DEBUG]" in line: css_class += " log-debug"
                log_display.mount(LogLine(line, classes=css_class)) # Mount the filtered log line as a widget

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when the filter input field's value changes, triggering a display update."""
        self.update_log_display()

    def action_clear_filter(self) -> None:
        """Action to clear the filter input field and refresh the display."""
        self.query_one("#filter-input", Input).value = ""
        self.update_log_display()
        self.query_one("#log-display").scroll_end() # Scroll to end after clearing filter

    def action_quit(self) -> None:
        """Action to quit the application."""
        self.exit()

if __name__ == "__main__":
    app = LogViewerApp()
    app.run()
