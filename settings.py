class Settings:
    """A class to store all setitngs for Alien Invasion."""

    def __init__(self):
        """Initialize the game's  static settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        #Ship settings
        self.ship_limit = 3

        #Bullet settings
        self.bullet_width = 3        
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5

        #Alien settings
        self.fleet_drop_speed = 10

        #Sound Settings
        self.bg_m = 0.7
        self.bg_mn = "music/inside1.wav"
        self.bg_s_s = "music/shoot.wav"
        self.bg_s_b = 'music/blast.wav'
        self.bg_s_st = 'music/start.wav'
    
        # How Quickly the game speeds up
        self.speedup_scale = 4
        self.initialize_dynamic_settings()
        
        # How quickly the alien point values increase
        self.score_scale = 1.5


    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.7
        self.bullet_speed = 2.2
        self.alien_speed = 1.2
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
            # Scoring settings
        self.alien_points = 50

    def increase_speed(self):
        """Increse speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
        