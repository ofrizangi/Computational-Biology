# Ofri Zangi 207488305

import pygame
import random
import matplotlib.pyplot as plt


def build_cellular_automat():
    cell_rows = []
    for i in range(0, 200):
        cell_col = [0] * 200
        cell_rows.append(cell_col)
    return cell_rows


def build_creatures_dictionary(number_of_creatures, automat_cells):
    creatures_position = {}
    for i in range(1, number_of_creatures + 1):
        place = (random.randint(0, 199), random.randint(0, 199))
        # in order to avoid duplicate creatures in the same cell at the first placement
        while automat_cells[place[0]][place[1]] == 1:
            place = (random.randint(0, 199), random.randint(0, 199))
        automat_cells[place[0]][place[1]] = 1
        creatures_position.update({i: place})
    return creatures_position


def choose_infected_creatures(number_of_creatures, num_of_infected, automat_cells, creature_place):
    list_of_infected_creatures = random.sample(range(1, number_of_creatures + 1), num_of_infected)
    for creature in list_of_infected_creatures:
        place = creature_place[creature]
        automat_cells[place[0]][place[1]] = 2
    return list_of_infected_creatures


def draw_creatures_on_screen(screen, creatures_position, infected_creatures, recovered_creatures):
    for key in creatures_position:
        place = creatures_position[key]
        if key in infected_creatures:
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(3 * place[1], 3 * place[0], 3, 3))
        elif key in recovered_creatures:
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(3 * place[1], 3 * place[0], 3, 3))
        else:
            pygame.draw.rect(screen, (0, 100, 0), pygame.Rect(3 * place[1], 3 * place[0], 3, 3))


def create_neighbors_places_list(place):
    neighbors = [place, ((place[0] - 1) % 200, (place[1]) % 200), (place[0] % 200, (place[1] - 1) % 200),
                 ((place[0] + 1) % 200, place[1] % 200),
                 (place[0] % 200, (place[1] + 1) % 200), ((place[0] + 1) % 200, (place[1] + 1) % 200),
                 ((place[0] - 1) % 200, (place[1] - 1) % 200), ((place[0] + 1) % 200, (place[1] - 1) % 200),
                 ((place[0] - 1) % 200, (place[1] + 1) % 200)]
    return neighbors


def place_in_next_generation(creatures_position, automat_cells, fast_creatures):
    for key in creatures_position:
        place = creatures_position[key]
        if key not in fast_creatures:
            options_of_places = create_neighbors_places_list(place)
        else:
            options_of_places = [place, ((place[0] - 10) % 200, (place[1]) % 200),
                                 (place[0] % 200, (place[1] - 10) % 200),
                                 ((place[0] + 10) % 200, place[1] % 200),
                                 (place[0] % 200, (place[1] + 10) % 200),
                                 ((place[0] + 10) % 200, (place[1] + 10) % 200),
                                 ((place[0] - 10) % 200, (place[1] - 10) % 200),
                                 ((place[0] + 10) % 200, (place[1] - 10) % 200),
                                 ((place[0] - 10) % 200, (place[1] + 10) % 200)]

        chosen_option = random.choice(options_of_places)
        """
        The code for avoiding duplicates in the same cell:
        if there is already a creature in this cell in this or the next generation, we will remove this option from the
        list and randomly choose a different one
        """
        while automat_cells[chosen_option[0]][chosen_option[1]] != 0 and chosen_option != place:
            options_of_places.remove(chosen_option)
            chosen_option = random.choice(options_of_places)

        if chosen_option != place:
            creatures_position[key] = chosen_option
            automat_cells[chosen_option[0]][chosen_option[1]] = automat_cells[place[0]][place[1]]
            automat_cells[place[0]][place[1]] = 0


#  only if the random number is smaller than the precision than we will get an infection
# that way it can happen only in a probability that is request
def decide_if_need_to_be_infected(precision_for_infection):
    num = random.random()
    if num <= precision_for_infection:
        return True
    return False


def check_if_infected(automat_cells, creatures_position, creatures_infected, precision_for_infection,
                      X_value, recoverd_creatures):
    first_added_position = -1
    for key in creatures_position:
        # a creature can be infected if he had not been sick already
        if key not in creatures_infected and key not in recoverd_creatures:
            position = creatures_position[key]
            neighbors = create_neighbors_places_list(position)
            for place in neighbors:
                if 2 <= automat_cells[place[0]][place[1]] < X_value + 2:
                    if decide_if_need_to_be_infected(precision_for_infection):
                        creatures_infected.append(key)
                        if first_added_position == -1:
                            first_added_position = len(creatures_infected) - 1
                        break
    return first_added_position


def update_infected_in_automat(automat_cells, creatures_position, creatures_infected, index_to_start,
                               recovered_creatures, X_value):
    for creature in creatures_infected:
        place = creatures_position[creature]
        # in any generation we raise the number of days the creature is sick by 1
        automat_cells[place[0]][place[1]] += 1
        # the creature got recovered
        if automat_cells[place[0]][place[1]] >= X_value + 2:
            recovered_creatures.append(creature)
            creatures_infected.remove(creature)
    return creatures_infected


def update_probability_to_be_infected(T_value, low_probability, high_probability, current_infected):
    if current_infected < T_value:
        return high_probability
    return low_probability


def show_graph(list_generation, list_infection):
    plt.plot(list_generation, list_infection)
    plt.ylabel('percent of current infected creatures')
    plt.xlabel('generation number')
    plt.show()


def activate_simulator(N, D, R, X, P_high, P_low, T):
    cellular_automat = build_cellular_automat()
    num_of_creatures = N
    D_percent_of_infected_creatures = D
    num_of_infected_creatures = int(float(num_of_creatures) * D_percent_of_infected_creatures)
    creatures_position_dict = build_creatures_dictionary(num_of_creatures, cellular_automat)
    all_infected_creatures = choose_infected_creatures(num_of_creatures, num_of_infected_creatures, cellular_automat,
                                                       creatures_position_dict)
    recovered_creatures = []
    # fast creatures
    R_percent_of_fast_creatures = R
    num_of_fast_creatures = int(float(num_of_creatures) * R_percent_of_fast_creatures)
    list_of_fast_creatures = random.sample(range(1, num_of_creatures + 1), num_of_fast_creatures)

    P_low_probability = P_low
    P_high_probability = P_high
    T_treshhold_value = T
    percent_of_infected_in_any_generation = D_percent_of_infected_creatures

    P_probability_of_infection = update_probability_to_be_infected(T_treshhold_value, P_low_probability,
                                                                   P_high_probability,
                                                                   percent_of_infected_in_any_generation)
    X_number_of_generation_for_infecting = X

    pygame.init()

    # Set up the drawing window
    screen = pygame.display.set_mode([600, 650])
    text = "percent of infected creatures in current generation:"
    num = str(D_percent_of_infected_creatures * 100) + "%"
    enter = "press enter to end the simulation (to see the graph go to the png file)"

    number_of_generation = 0
    list_of_percent_infection = [percent_of_infected_in_any_generation]
    list_of_generations = [number_of_generation]

    running = True
    while running:

        # If the user click the window close button
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                show_graph(list_of_generations, list_of_percent_infection)
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if running:
                        show_graph(list_of_generations, list_of_percent_infection)
                        running = False
                        break

        # Fill the background with white
        screen.fill((255, 255, 255))
        base_font = pygame.font.SysFont('Comic Sans MS', 16)
        text_surface = base_font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (5, 600))

        text_surface = base_font.render(num, True, (0, 0, 0))
        screen.blit(text_surface, (410, 600))

        base_font = pygame.font.SysFont('Comic Sans MS', 14)
        text_surface = base_font.render(enter, True, (255, 0, 0))
        screen.blit(text_surface, (80, 620))

        draw_creatures_on_screen(screen, creatures_position_dict, all_infected_creatures, recovered_creatures)

        pygame.display.update()
        # Flip the display
        pygame.display.flip()

        # Calling the functions that operate the simulation
        index_to_start_updating_creatures = check_if_infected(cellular_automat, creatures_position_dict,
                                                              all_infected_creatures, P_probability_of_infection,
                                                              X_number_of_generation_for_infecting, recovered_creatures)
        all_infected_creatures = update_infected_in_automat(cellular_automat, creatures_position_dict,
                                                            all_infected_creatures,
                                                            index_to_start_updating_creatures, recovered_creatures,
                                                            X_number_of_generation_for_infecting)
        place_in_next_generation(creatures_position_dict, cellular_automat, list_of_fast_creatures)

        percent_of_infected_in_any_generation = float(len(all_infected_creatures)) / float(num_of_creatures)
        P_probability_of_infection = update_probability_to_be_infected(T_treshhold_value, P_low_probability,
                                                                       P_high_probability,
                                                                       percent_of_infected_in_any_generation)
        number_of_generation += 1
        list_of_generations.append(number_of_generation)
        list_of_percent_infection.append(percent_of_infected_in_any_generation)
        num = str(percent_of_infected_in_any_generation * 100) + "%"

    # Done! Time to quit.
    pygame.quit()


if __name__ == '__main__':

    pygame.init()
    pygame.font.init()  # you have to call this at the start,

    # Set up the drawing window
    screen = pygame.display.set_mode([600, 600])
    base_font = pygame.font.SysFont('Comic Sans MS', 26)
    title = "Change parameter values here:"
    end = "Press enter to go to the simulation"

    # parameters we want to allow the user to change
    text_to_print = ["N: ", "D:", "R:", "X:", "High value of P:", "Low value of P:", "T:"]
    inputs = [["9000", pygame.Rect(250, 90, 200, 32), False], ["0.01", pygame.Rect(250, 160, 200, 32), False],
              ["0.8", pygame.Rect(250, 230, 200, 32), False], ["5", pygame.Rect(250, 300, 200, 32), False],
              ["0.7", pygame.Rect(250, 370, 200, 32), False], ["0.001", pygame.Rect(250, 440, 200, 32), False],
              ["0.08", pygame.Rect(250, 510, 200, 32), False]]

    running = True
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for my_input in inputs:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # check if the position of the box and the click colide
                    if my_input[1].collidepoint(event.pos):
                        my_input[2] = True
                    else:
                        my_input[2] = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if running:
                            activate_simulator(int(inputs[0][0]), float(inputs[1][0]), float(inputs[2][0]),
                                               int(inputs[3][0]), float(inputs[4][0]), float(inputs[5][0]),
                                               float(inputs[6][0]))
                        running = False

                    if my_input[2]:
                        if event.key == pygame.K_BACKSPACE:
                            my_input[0] = my_input[0][0:-1]
                        else:
                            my_input[0] += event.unicode

        # Fill the background with white
        screen.fill((255, 255, 255))

        text_surface_tile = base_font.render(title, True, (0, 0, 0))
        screen.blit(text_surface_tile, (50, 30))

        y_pos = 0
        for name in text_to_print:
            text_surface = base_font.render(name, True, (0, 0, 0))
            screen.blit(text_surface, (50, 90 + y_pos))
            y_pos += 70

        for my_input in inputs:
            text_surface = base_font.render(my_input[0], True, (0, 0, 0))
            screen.blit(text_surface, (my_input[1].x + 10, my_input[1].y - 2))
            my_input[1].w = max(text_surface.get_width() + 10, 200)
            pygame.draw.rect(screen, (255, 0, 0), my_input[1], 2)

        text_surface_tile = base_font.render(end, True, (0, 0, 0))
        screen.blit(text_surface_tile, (100, 560))

        pygame.display.update()
        # Flip the display
        pygame.display.flip()
