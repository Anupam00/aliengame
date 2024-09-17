#Creating a Pygame Window
import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    '''Overall class to manage game assets and behaviour.'''

    def __init__(self):
        """Initialize the game and create game"""
        pygame.init()
        self.bg_m = pygame.mixer.music
        self.bg_s =pygame.mixer.Sound
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        #Create an instance to store game statistics and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Set Background color
        self.bg_color = (self.settings.bg_color)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()

        # Start Alien Invasion in an active state.
        self.game_active = False

        # Make the Play button.
        self.play_button = Button(self,"Play")

        #Start background  music
        self.bg_music()



    def run_game(self):
        """Set the main loop for the game"""   
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)

    def bg_music(self):
            """Background music of the game"""
            self.bg_m.load(self.settings.bg_mn)
            self.bg_m.set_volume(self.settings.bg_m)
            self.bg_m.play(loops=10)    

    def _check_events(self):
            """Respond to keypresses and mouse events."""
            #Watch for keyboard and mouse events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit( )
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type ==pygame.KEYUP:
                    self._check_keyup_events(event)  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
    
    def _check_play_button(self,mouse_pos):
        """Start a new game when the player clicks play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game statistics.
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            # Create an new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            #Adjust Music 
            self._update_music()
            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _update_music(self):
        "Updating music of the game"
        self.settings.bg_mn = "music/inside.wav" 
        self.settings.bg_m = 0.4
        # starting sound
        start =self.bg_s(self.settings.bg_s_st)
        start.play()
        self.bg_music()

    def _check_keydown_events(self,event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            #move ship to the right
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            #move ship to the left
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _fire_bullet(self):
        """Create a new bullet anf add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            #Shooting effects
            shoot = self.bg_s(self.settings.bg_s_s)
            shoot.play()

    def _check_keyup_events(self,event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _update_bullets(self):
        """Update position of the bullets and get rid of the old bullets."""
        #Update bullet positions.
        self.bullets.update()
        #Get rid bullets that have disappeared.
        for bullet in self.bullets.copy():
                if bullet.rect.bottom <=0:
                    self.bullets.remove(bullet)
        self._check_bullet_alien_collision()
        self._level_up()

    def _check_bullet_alien_collision(self):           
        # Check for any bullets that have hit aliens.
        #If so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide( self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points *len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            #blasting effect
            blast = self.bg_s(self.settings.bg_s_b)
            blast.play()

    def _level_up(self):
        # Refill the aliens if all aliens are destroyed!!
        if not self.aliens:
            # Destory existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            #Incresae game elemetns speed as level progress
            self.settings.increase_speed()
            #Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        "Update the positions of all aliens in the fleet"
        self._check_fleet_edges()
        self.aliens.update()
        
        #Look for alien - ship collision.
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ship_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            # Pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #Treat this the same as if the ship got hit.
                self._ship_hit()

    def _update_screen(self):
            # Redraw the screen during each pass through the loop
            self.screen.fill(self.bg_color)
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            # Draw ship
            self.ship.blitme()
            self.aliens.draw(self.screen)
            # Draw the score information.
            self.sb.show_score()
            # Draw the play button if the game is inactive.
            if not self.game_active:
                self.play_button.draw_button()
            # Make the most recently drawn screen visible.
            pygame.display.flip()

    def _create_fleet(self):
        """Create the fleet of aliens. """
        # Make an alien.
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y =alien_width, alien_height

        while current_y < (self.settings.screen_height - 5 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):   
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            
            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height


    def _create_alien(self,x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


if __name__ == '__main__':
    #Make a game instance and run the game
    ai = AlienInvasion()
    ai.run_game()
