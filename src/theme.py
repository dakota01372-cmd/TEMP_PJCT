"""
Theme management for TigerMemory GUI.

Provides light and dark color schemes with easy switching and persistence.
"""

import json
from pathlib import Path


class ThemeManager:
    """Manages GUI color themes."""
    
    # Light theme
    LIGHT_THEME = {
        "name": "light",
        "bg": "#ffffff",
        "fg": "#000000",
        "frame_bg": "#f0f0f0",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "button_bg": "#e0e0e0",
        "button_fg": "#000000",
        "button_hover": "#d0d0d0",
        "label_bg": "#f0f0f0",
        "label_fg": "#000000",
        "text_bg": "#ffffff",
        "text_fg": "#000000",
        "tree_bg": "#ffffff",
        "tree_fg": "#000000",
        "tree_heading_bg": "#d0d0d0",
        "tree_heading_fg": "#000000",
        "tree_select": "#0078d7",
        "status_bg": "#e0e0e0",
        "status_fg": "#000000",
        "accent": "#0078d7",
    }
    
    # Dark theme
    DARK_THEME = {
        "name": "dark",
        "bg": "#1e1e1e",
        "fg": "#e0e0e0",
        "frame_bg": "#2d2d2d",
        "entry_bg": "#3e3e3e",
        "entry_fg": "#e0e0e0",
        "button_bg": "#404040",
        "button_fg": "#e0e0e0",
        "button_hover": "#505050",
        "label_bg": "#2d2d2d",
        "label_fg": "#e0e0e0",
        "text_bg": "#2d2d2d",
        "text_fg": "#e0e0e0",
        "tree_bg": "#3e3e3e",
        "tree_fg": "#e0e0e0",
        "tree_heading_bg": "#404040",
        "tree_heading_fg": "#e0e0e0",
        "tree_select": "#0078d7",
        "status_bg": "#2d2d2d",
        "status_fg": "#e0e0e0",
        "accent": "#0078d7",
    }
    
    def __init__(self, config_path: Path = None):
        """Initialize theme manager.
        
        Args:
            config_path: Path to config directory. If None, uses config directory.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config"
        
        self.config_path = config_path
        self.config_path.mkdir(exist_ok=True)
        self.theme_file = self.config_path / "theme_config.json"
        
        # Load current theme
        self.current_theme = self._load_theme()
    
    def _load_theme(self) -> dict:
        """Load theme from config file or use default (light)."""
        if self.theme_file.exists():
            try:
                with open(self.theme_file, "r") as f:
                    config = json.load(f)
                    theme_name = config.get("theme", "light")
                    return self.get_theme(theme_name)
            except Exception:
                return self.LIGHT_THEME.copy()
        return self.LIGHT_THEME.copy()
    
    def save_theme(self, theme_name: str) -> None:
        """Save theme preference to config file.
        
        Args:
            theme_name: "light" or "dark"
        """
        config = {"theme": theme_name}
        with open(self.theme_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def get_theme(self, theme_name: str) -> dict:
        """Get theme by name.
        
        Args:
            theme_name: "light" or "dark"
        
        Returns:
            Dictionary with color scheme
        """
        if theme_name == "dark":
            return self.DARK_THEME.copy()
        return self.LIGHT_THEME.copy()
    
    def set_theme(self, theme_name: str) -> None:
        """Set current theme and save preference.
        
        Args:
            theme_name: "light" or "dark"
        """
        self.current_theme = self.get_theme(theme_name)
        self.save_theme(theme_name)
    
    def get_color(self, key: str) -> str:
        """Get color value from current theme.
        
        Args:
            key: Color key (e.g., "bg", "fg", "accent")
        
        Returns:
            Hex color string
        """
        return self.current_theme.get(key, "#000000")
    
    def apply_to_widget(self, widget, bg=True, fg=True, insert_color=False) -> None:
        """Apply current theme colors to a tkinter widget.
        
        Args:
            widget: tkinter widget
            bg: Apply background color
            fg: Apply foreground color
            insert_color: For Entry widgets, apply insert (cursor) color
        """
        try:
            if bg and hasattr(widget, "configure"):
                # Determine appropriate background color
                widget_type = type(widget).__name__
                
                if widget_type in ("Entry", "Text", "Spinbox"):
                    bg_color = self.get_color("entry_bg")
                elif widget_type == "Treeview":
                    bg_color = self.get_color("tree_bg")
                else:
                    bg_color = self.get_color("frame_bg")
                
                widget.configure(bg=bg_color)
            
            if fg and hasattr(widget, "configure"):
                widget_type = type(widget).__name__
                if widget_type not in ("Frame", "LabelFrame"):
                    fg_color = self.get_color("fg")
                    widget.configure(fg=fg_color)
            
            if insert_color and hasattr(widget, "configure"):
                if type(widget).__name__ in ("Entry", "Text", "Spinbox"):
                    widget.configure(insertbackground=self.get_color("fg"))
        
        except Exception:
            pass  # Silently fail if widget doesn't support that option


# Global theme manager instance
_theme_manager = None


def get_theme_manager(config_path: Path = None) -> ThemeManager:
    """Get or create global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(config_path)
    return _theme_manager
