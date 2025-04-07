"""
Configuration editor module for the Chakram X controller using Tkinter.
Provides a GUI for editing the controller configuration.
"""

import sys
import os
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox
from src.config import SECTORS, KEY_MAPPINGS, DEADZONE, DEADZONE_SPEED_THRESHOLD, RELEASE_DELAY, SECTOR_CHANGE_COOLDOWN, VISUALIZATION

class ConfigEditor:
    def __init__(self, root):
        """Initialize the configuration editor."""
        self.root = root
        self.root.title("Chakram X Controller Configuration Editor")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Load the current configuration
        self.config = {
            "deadzone": DEADZONE,
            "deadzone_speed_threshold": DEADZONE_SPEED_THRESHOLD,
            "release_delay": RELEASE_DELAY,
            "sector_change_cooldown": SECTOR_CHANGE_COOLDOWN,
            "sectors": SECTORS,
            "key_mappings": KEY_MAPPINGS,
            "visualization": VISUALIZATION
        }
        
        # Create a frame for the preview and settings
        self.split_frame = ttk.Frame(self.root)
        self.split_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the preview frame on the right
        self.preview_frame = ttk.LabelFrame(self.split_frame, text="Preview")
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the canvas for the joystick visualization
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="#1E1E1E", width=300, height=300)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the settings frame on the left with scrollbar
        self.settings_outer_frame = ttk.Frame(self.split_frame)
        self.settings_outer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.settings_outer_frame)
        self.scrollbar = ttk.Scrollbar(self.settings_outer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for the content
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW)
        
        # Configure the canvas to resize with the window
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.content_frame.bind('<Configure>', self.on_frame_configure)
        
        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Create the UI elements in the content frame
        self.create_ui()
        
        # Create the button frame at the bottom
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create the buttons
        self.save_button = ttk.Button(self.button_frame, text="Save Configuration", command=self.save_configuration)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(self.button_frame, text="Reset to Defaults", command=self.reset_to_defaults)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = ttk.Button(self.button_frame, text="Exit Without Saving", command=self.root.destroy)
        self.exit_button.pack(side=tk.RIGHT, padx=5)
        
        # Start the update loop for the preview
        self.update_preview()
    
    def on_canvas_configure(self, event):
        """Handle canvas resize event."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_frame_configure(self, event):
        """Handle content frame resize event."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_ui(self):
        """Create the UI elements."""
        # Create a title
        title_label = ttk.Label(self.content_frame, text="Chakram X Controller Configuration Editor", font=("Arial", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Create the basic settings section
        basic_frame = ttk.LabelFrame(self.content_frame, text="Basic Settings")
        basic_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        
        # Deadzone slider
        ttk.Label(basic_frame, text="Deadzone:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.deadzone_var = tk.DoubleVar(value=self.config["deadzone"])
        self.deadzone_slider = ttk.Scale(basic_frame, from_=0.0, to=0.5, variable=self.deadzone_var, orient=tk.HORIZONTAL, length=300)
        self.deadzone_slider.grid(row=0, column=1, padx=5, pady=5)
        self.deadzone_label = ttk.Label(basic_frame, text=f"{self.config['deadzone']:.2f}")
        self.deadzone_label.grid(row=0, column=2, padx=5, pady=5)
        self.deadzone_var.trace_add("write", lambda *args: self.update_deadzone_label())
        
        # Deadzone speed threshold slider
        ttk.Label(basic_frame, text="Deadzone Speed Threshold:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.deadzone_speed_threshold_var = tk.DoubleVar(value=self.config["deadzone_speed_threshold"])
        self.deadzone_speed_threshold_slider = ttk.Scale(basic_frame, from_=0.5, to=5.0, variable=self.deadzone_speed_threshold_var, orient=tk.HORIZONTAL, length=300)
        self.deadzone_speed_threshold_slider.grid(row=1, column=1, padx=5, pady=5)
        self.deadzone_speed_threshold_label = ttk.Label(basic_frame, text=f"{self.config['deadzone_speed_threshold']:.2f}")
        self.deadzone_speed_threshold_label.grid(row=1, column=2, padx=5, pady=5)
        self.deadzone_speed_threshold_var.trace_add("write", lambda *args: self.deadzone_speed_threshold_label.config(text=f"{self.deadzone_speed_threshold_var.get():.2f}"))
        
        # Release delay slider
        ttk.Label(basic_frame, text="Release Delay (seconds):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.release_delay_var = tk.DoubleVar(value=self.config["release_delay"])
        self.release_delay_slider = ttk.Scale(basic_frame, from_=0.0, to=0.2, variable=self.release_delay_var, orient=tk.HORIZONTAL, length=300)
        self.release_delay_slider.grid(row=2, column=1, padx=5, pady=5)
        self.release_delay_label = ttk.Label(basic_frame, text=f"{self.config['release_delay']:.2f}")
        self.release_delay_label.grid(row=2, column=2, padx=5, pady=5)
        self.release_delay_var.trace_add("write", lambda *args: self.release_delay_label.config(text=f"{self.release_delay_var.get():.2f}"))
        
        # Sector change cooldown slider
        ttk.Label(basic_frame, text="Sector Change Cooldown (seconds):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.sector_change_cooldown_var = tk.DoubleVar(value=self.config["sector_change_cooldown"])
        self.sector_change_cooldown_slider = ttk.Scale(basic_frame, from_=0.05, to=0.3, variable=self.sector_change_cooldown_var, orient=tk.HORIZONTAL, length=300)
        self.sector_change_cooldown_slider.grid(row=3, column=1, padx=5, pady=5)
        self.sector_change_cooldown_label = ttk.Label(basic_frame, text=f"{self.config['sector_change_cooldown']:.2f}")
        self.sector_change_cooldown_label.grid(row=3, column=2, padx=5, pady=5)
        self.sector_change_cooldown_var.trace_add("write", lambda *args: self.sector_change_cooldown_label.config(text=f"{self.sector_change_cooldown_var.get():.2f}"))
        
        # Create the sector boundaries section
        sectors_frame = ttk.LabelFrame(self.content_frame, text="Sector Boundaries")
        sectors_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        
        # Create a frame for each sector
        self.sector_frames = {}
        self.sector_vars = {}
        
        row = 0
        for sector_name in SECTORS:
            # Create a frame for this sector
            sector_frame = ttk.LabelFrame(sectors_frame, text=f"{sector_name.capitalize()} Sector")
            sector_frame.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
            self.sector_frames[sector_name] = sector_frame
            
            # Create variables for this sector
            self.sector_vars[sector_name] = {
                "start": tk.DoubleVar(value=self.config["sectors"][sector_name]["start"]),
                "end": tk.DoubleVar(value=self.config["sectors"][sector_name]["end"])
            }
            
            # Sector start angle
            ttk.Label(sector_frame, text="Start Angle:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            start_slider = ttk.Scale(sector_frame, from_=0, to=360, variable=self.sector_vars[sector_name]["start"], orient=tk.HORIZONTAL, length=300)
            start_slider.grid(row=0, column=1, padx=5, pady=5)
            start_label = ttk.Label(sector_frame, text=f"{self.sector_vars[sector_name]['start'].get():.1f}°")
            start_label.grid(row=0, column=2, padx=5, pady=5)
            self.sector_vars[sector_name]["start"].trace_add("write", lambda *args, label=start_label, var=self.sector_vars[sector_name]["start"]: 
                                                            self.update_sector_label(label, var))
            
            # Sector end angle
            ttk.Label(sector_frame, text="End Angle:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            end_slider = ttk.Scale(sector_frame, from_=0, to=360, variable=self.sector_vars[sector_name]["end"], orient=tk.HORIZONTAL, length=300)
            end_slider.grid(row=1, column=1, padx=5, pady=5)
            end_label = ttk.Label(sector_frame, text=f"{self.sector_vars[sector_name]['end'].get():.1f}°")
            end_label.grid(row=1, column=2, padx=5, pady=5)
            self.sector_vars[sector_name]["end"].trace_add("write", lambda *args, label=end_label, var=self.sector_vars[sector_name]["end"]: 
                                                          self.update_sector_label(label, var))
            
            row += 1
        
        # Create the key mappings section
        keys_frame = ttk.LabelFrame(self.content_frame, text="Key Mappings")
        keys_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        
        # Create variables for key mappings
        self.key_vars = {}
        
        row = 0
        for action, key in KEY_MAPPINGS.items():
            ttk.Label(keys_frame, text=f"{action.capitalize()} Key:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            self.key_vars[action] = tk.StringVar(value=key)
            key_entry = ttk.Entry(keys_frame, textvariable=self.key_vars[action], width=10)
            key_entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Create a button to capture key press
            capture_button = ttk.Button(keys_frame, text="Capture", command=lambda action=action: self.capture_key(action))
            capture_button.grid(row=row, column=2, padx=5, pady=5)
            
            row += 1
        
        # Create the visualization settings section
        vis_frame = ttk.LabelFrame(self.content_frame, text="Visualization Settings")
        vis_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        
        # Create variables for visualization settings
        self.vis_vars = {
            "window_size": {
                "width": tk.IntVar(value=self.config["visualization"]["window_size"][0]),
                "height": tk.IntVar(value=self.config["visualization"]["window_size"][1])
            }
        }
        
        # Window size
        ttk.Label(vis_frame, text="Window Size:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        size_frame = ttk.Frame(vis_frame)
        size_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        width_entry = ttk.Entry(size_frame, textvariable=self.vis_vars["window_size"]["width"], width=5)
        width_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(size_frame, text="Height:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        height_entry = ttk.Entry(size_frame, textvariable=self.vis_vars["window_size"]["height"], width=5)
        height_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
    
    def update_deadzone_label(self):
        """Update the deadzone label and refresh the preview."""
        self.deadzone_label.config(text=f"{self.deadzone_var.get():.2f}")
        self.update_preview()
    
    def capture_key(self, action):
        """Capture a key press for the given action."""
        # Create a top-level window for key capture
        capture_window = tk.Toplevel(self.root)
        capture_window.title("Capture Key")
        capture_window.geometry("300x150")
        capture_window.transient(self.root)
        capture_window.grab_set()
        
        # Create a label with instructions
        ttk.Label(capture_window, text=f"Press any key for {action}...\n(ESC to cancel)").pack(pady=10)
        
        # Add special button for middle mouse if this is the cancel action
        if action == "cancel":
            ttk.Label(capture_window, text="Or select special input:").pack(pady=5)
            middle_mouse_button = ttk.Button(
                capture_window, 
                text="Middle Mouse Button", 
                command=lambda: [self.key_vars[action].set("middle_mouse"), capture_window.destroy()]
            )
            middle_mouse_button.pack(pady=5)
        
        # Bind key press event
        def on_key_press(event):
            if event.keysym == "Escape":
                capture_window.destroy()
                return
            
            # Set the key variable
            self.key_vars[action].set(event.keysym)
            capture_window.destroy()
        
        capture_window.bind("<Key>", on_key_press)
    
    def save_configuration(self):
        """Save the configuration to a file."""
        # Update the configuration from the UI elements
        self.config["deadzone"] = self.deadzone_var.get()
        self.config["deadzone_speed_threshold"] = self.deadzone_speed_threshold_var.get()
        self.config["release_delay"] = self.release_delay_var.get()
        self.config["sector_change_cooldown"] = self.sector_change_cooldown_var.get()
        
        # Update sectors
        for sector_name in SECTORS:
            self.config["sectors"][sector_name]["start"] = self.sector_vars[sector_name]["start"].get()
            self.config["sectors"][sector_name]["end"] = self.sector_vars[sector_name]["end"].get()
        
        # Update key mappings
        for action in KEY_MAPPINGS:
            self.config["key_mappings"][action] = self.key_vars[action].get()
        
        # Update visualization settings
        self.config["visualization"]["window_size"] = (
            self.vis_vars["window_size"]["width"].get(),
            self.vis_vars["window_size"]["height"].get()
        )
        
        # Create the config directory if it doesn't exist
        config_dir = os.path.join(os.path.expanduser("~"), ".chakram_controller")
        os.makedirs(config_dir, exist_ok=True)
        
        # Save the configuration to a file
        config_path = os.path.join(config_dir, "config.json")
        
        try:
            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved successfully to {config_path}")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration: {e}")
    
    def reset_to_defaults(self):
        """Reset the configuration to defaults."""
        # Reset deadzone
        self.deadzone_var.set(DEADZONE)
        
        # Reset deadzone speed threshold
        self.deadzone_speed_threshold_var.set(DEADZONE_SPEED_THRESHOLD)
        
        # Reset release delay
        self.release_delay_var.set(RELEASE_DELAY)
        
        # Reset sector change cooldown
        self.sector_change_cooldown_var.set(SECTOR_CHANGE_COOLDOWN)
        
        # Reset sectors
        for sector_name in SECTORS:
            self.sector_vars[sector_name]["start"].set(SECTORS[sector_name]["start"])
            self.sector_vars[sector_name]["end"].set(SECTORS[sector_name]["end"])
        
        # Reset key mappings
        for action, key in KEY_MAPPINGS.items():
            self.key_vars[action].set(key)
        
        # Reset visualization settings
        self.vis_vars["window_size"]["width"].set(VISUALIZATION["window_size"][0])
        self.vis_vars["window_size"]["height"].set(VISUALIZATION["window_size"][1])
        
        messagebox.showinfo("Reset", "Configuration reset to defaults.")
    
    def update_sector_label(self, label, var):
        """Update a sector angle label and refresh the preview."""
        label.config(text=f"{var.get():.1f}°")
        self.update_preview()
    
    def update_preview(self):
        """Update the joystick visualization preview."""
        # Clear the canvas
        self.preview_canvas.delete("all")
        
        # Get the canvas dimensions
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Ensure the canvas has a minimum size
        if canvas_width < 50 or canvas_height < 50:
            self.root.after(100, self.update_preview)
            return
        
        # Calculate the center of the canvas
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        # Calculate the radius of the joystick area
        radius = min(center_x, center_y) - 20
        
        # Draw the sectors
        for sector_name in self.sector_vars:
            start_angle = self.sector_vars[sector_name]["start"].get()
            end_angle = self.sector_vars[sector_name]["end"].get()
            
            # Get the sector color
            sector_color = "#{:02x}{:02x}{:02x}".format(*VISUALIZATION["sector_colors"].get(sector_name, (100, 100, 100)))
            
            # Handle sector that wraps around 0°
            if start_angle > end_angle:
                # Draw from start_angle to 360°
                self.preview_canvas.create_arc(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    start=start_angle, extent=360 - start_angle,
                    outline="", fill=sector_color, tags="sector"
                )
                # Draw from 0° to end_angle
                self.preview_canvas.create_arc(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    start=0, extent=end_angle,
                    outline="", fill=sector_color, tags="sector"
                )
            else:
                self.preview_canvas.create_arc(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    start=start_angle, extent=end_angle - start_angle,
                    outline="", fill=sector_color, tags="sector"
                )
            
            # Draw sector label
            mid_angle = (start_angle + end_angle) / 2
            if start_angle > end_angle:
                mid_angle = (start_angle + end_angle + 360) / 2
                if mid_angle >= 360:
                    mid_angle -= 360
                    
            label_x = center_x + int(radius * 0.7 * math.cos(math.radians(mid_angle)))
            label_y = center_y + int(radius * 0.7 * math.sin(math.radians(mid_angle)))
            
            self.preview_canvas.create_text(label_x, label_y, text=sector_name, fill="#FFFFFF", tags="label")
        
        # Draw the deadzone circle
        deadzone_radius = radius * self.deadzone_var.get()
        self.preview_canvas.create_oval(
            center_x - deadzone_radius, center_y - deadzone_radius,
            center_x + deadzone_radius, center_y + deadzone_radius,
            outline="#444444", fill="#333333", tags="deadzone"
        )
        
        # Draw the sector boundary lines
        for sector_name in self.sector_vars:
            start_angle = self.sector_vars[sector_name]["start"].get()
            end_angle = self.sector_vars[sector_name]["end"].get()
            
            # Draw start angle line
            start_x = center_x + radius * math.cos(math.radians(start_angle))
            start_y = center_y + radius * math.sin(math.radians(start_angle))
            deadzone_x = center_x + deadzone_radius * math.cos(math.radians(start_angle))
            deadzone_y = center_y + deadzone_radius * math.sin(math.radians(start_angle))
            
            self.preview_canvas.create_line(
                deadzone_x, deadzone_y,
                start_x, start_y,
                fill="#FF0000", width=2, tags="boundary"
            )
            
            # Draw end angle line
            end_x = center_x + radius * math.cos(math.radians(end_angle))
            end_y = center_y + radius * math.sin(math.radians(end_angle))
            deadzone_x = center_x + deadzone_radius * math.cos(math.radians(end_angle))
            deadzone_y = center_y + deadzone_radius * math.sin(math.radians(end_angle))
            
            self.preview_canvas.create_line(
                deadzone_x, deadzone_y,
                end_x, end_y,
                fill="#FF0000", width=2, tags="boundary"
            )
        
        # Draw the center point
        self.preview_canvas.create_oval(
            center_x - 3, center_y - 3,
            center_x + 3, center_y + 3,
            outline="", fill="#FFFFFF", tags="center"
        )
        
        # Schedule the next update
        self.root.after(100, self.update_preview)

def run_config_editor():
    """Run the configuration editor."""
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()

if __name__ == "__main__":
    run_config_editor()
