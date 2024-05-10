import tkinter as tk
from tkinter import ttk, messagebox

from network_modules.server import Server
from network_modules.utils import FormGenerator


class Application:
    def __init__(self, window_width, window_height):
        self.__window = tk.Tk()
        self.__window.title("Réseau")

        self.window_width = window_width
        self.window_height = window_height
        self.__window.resizable(False, False)
        self.__center_window()

        self.__create_search_bar()
        self.__canvas = tk.Canvas(self.__window, width=window_width, height=window_height)
        self.__canvas.bind("<Button-3>", self.__handle_right_click)
        self.__canvas.pack()

        self.__research_starting_point = None  # Le serveur qui sera le point de départ des recherches
        self.servers = []
        self.__init_servers()

    def __init_servers(self):
        server1 = Server(self, 90, 80, "192.168.1.1")
        self.servers.append(server1)
        server1.draw(self.__canvas)
        server1.sites = "wikipedia.org"

        server2 = Server(self, 500, 400, "192.168.1.2")
        self.servers.append(server2)
        server2.draw(self.__canvas)
        server2.sites = "facebook.com;python.org"

        server3 = Server(self, 400, 100, "192.168.1.3")
        self.servers.append(server3)
        server3.draw(self.__canvas)
        server3.sites = "facebook.com;youtube.com;yahoo.fr"

        server1.add_neighbour(server2, "5", self.__canvas)
        server1.add_neighbour(server3, "10", self.__canvas)

    @property
    def window_width(self):
        return self.__window_width

    @window_width.setter
    def window_width(self, width):
        if not isinstance(width, int):
            raise TypeError("width doit être de type \"int\"")

        if width <= 0:
            raise ValueError("width doit être strictement positif")

        self.__window_width = width

    @property
    def window_height(self):
        return self.__window_height

    @window_height.setter
    def window_height(self, height):
        if not isinstance(height, int):
            raise TypeError("height doit être de type \"int\"")

        if height <= 0:
            raise ValueError("height doit être strictement positif")

        self.__window_height = height

    def __center_window(self):
        x = (self.__window.winfo_screenwidth() - self.__window_width) // 2
        y = (self.__window.winfo_screenheight() - self.__window_height) // 2

        self.__window.geometry(f"{self.__window_width}x{self.__window_height}+{x}+{y}")

    def __create_search_bar(self):
        search_frame = ttk.Frame(self.__window)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.insert(0, "Entrer un nom de domaine")
        search_entry.config(font=("Segoe UI", 10))

        search_button = ttk.Button(search_frame, text="Rechercher",
                                   command=lambda: self.__process_research(search_entry.get()), padding=(10, 2))
        search_button.pack(side=tk.LEFT, padx=5)
        reset_button = ttk.Button(search_frame, text="Reset", command=lambda: self.__reset(search_entry),
                                  padding=(10, 2))
        reset_button.pack(side=tk.LEFT)

    def __process_research(self, researched_domain):
        for server in self.servers:
            server.reset(self.__canvas)

        if self.__research_starting_point is None:
            messagebox.showerror("Error", "Préciser d'abord le point de départ des recherches")
            return

        researched_domain = researched_domain.strip()
        if researched_domain == "Entrer un nom de domaine" or researched_domain == "":
            messagebox.showerror("Error", "Veuillez préciser le nom de domaine à rechercher")
            return

        print(f"Domaine recherché : {researched_domain}")
        hosting_servers = self.__get_servers_that_host_domain(researched_domain)
        if len(hosting_servers) == 0:
            messagebox.showwarning("Attention",
                                   f"Aucun serveur n'hébèrge le site que vous avez recherché : {researched_domain}")
            return

        # Résultats des recherches
        shortest_path = self.__shortest_path(hosting_servers)
        if shortest_path is None:
            messagebox.showwarning("Attention",
                                   f"Le site {researched_domain} n'est pas accessible depuis le serveur "
                                   f"{self.__research_starting_point}")
            return

        for sp in shortest_path:
            sp.change_color(self.__canvas)

        print(f"Bienvenue sur {researched_domain}. Vous êtes dans le serveur {shortest_path[0]}")

    def __reset(self, search_entry):
        for server in self.servers:
            server.reset(self.__canvas)
            server.start(self.__canvas)

        search_entry.delete(0, 'end')
        search_entry.insert(0, "Entrer un nom de domaine")
        self.__research_starting_point = None

    def __get_servers_that_host_domain(self, researched_domain):
        results = []
        for server in self.servers:
            if server.is_active() is True and researched_domain in server.sites:
                results.append(server)

        return results

    def __dijkstra(self, destination_server):
        distances = {}
        predecessors = {}
        for s in self.servers:
            distances[s] = float("inf")
            predecessors[s] = None

        distances[self.__research_starting_point] = 0
        E = []
        F = set(self.servers)

        while F:
            u = min(F, key=lambda x: distances[x])
            F.remove(u)
            E.append(u)

            if u.is_active() is False:
                continue

            for v, w in u.get_neighbours():
                if distances[v] > distances[u] + w:
                    distances[v] = distances[u] + w
                    predecessors[v] = u

        return E, predecessors, distances

    def __shortest_path(self, hosting_servers):
        shortest_distance = float("inf")
        shortest_path = None

        for s in hosting_servers:
            E, predecessors, distances = self.__dijkstra(destination_server=s)

            if distances[s] < shortest_distance:
                shortest_distance = distances[s]

                shortest_path = []
                curr_server = s
                while predecessors[curr_server] is not None:
                    shortest_path.append(curr_server)
                    curr_server = predecessors[curr_server]
                shortest_path.append(self.__research_starting_point)

        return shortest_path

    def __handle_right_click(self, event):
        clicked_x = event.x
        clicked_y = event.y

        for server in self.servers:
            if server.is_within_bounds(clicked_x, clicked_y) is True:
                context_menu = tk.Menu(self.__window, tearoff=0)
                context_menu.add_command(label="Ajoutes des sites",
                                         command=lambda: self.__add_urls(server, event.x, event.y))
                context_menu.add_command(label="Établir une liaison avec d'autres serveurs",
                                         command=lambda: self.__establish_connection(server, event.x, event.y))

                if self.__research_starting_point != server and server.is_active() is True:
                    context_menu.add_command(label="Marquer comme point de départ",
                                             command=lambda: self.__mark_as_research_starting_point(server))

                if server.is_active():
                    label = "Arrêter le serveur"
                    action = server.stop
                else:
                    label = "Démarrer le serveur"
                    action = server.start
                context_menu.add_command(label=f"{label}", command=lambda: action(self.__canvas))

                context_menu.post(event.x_root, event.y_root)
                return

        context_menu = tk.Menu(self.__window, tearoff=0)
        context_menu.add_command(label="Créer un serveur", command=lambda: self.__add_server(event.x, event.y))
        context_menu.post(event.x_root, event.y_root)

    def __add_server(self, center_x, center_y):
        def validate(form_controls):
            server = Server(self, center_x, center_y, form_controls["Adresse IP"].get())
            self.servers.append(server)
            server.draw(self.__canvas)

        (FormGenerator(self.__window, center_x, center_y, "Création d'un serveur",
                       [("Adresse IP", "entry")])
         .build_form(validate))

    def __add_urls(self, server, x, y):
        def validate(form_controls):
            server.sites = form_controls["Sites"].get("1.0", "end-1c")

        (FormGenerator(self.__window, x, y, "Ajout de sites", [("Sites", "textarea")])
         .build_form(validate))

    def __get_available_servers(self, server):
        servers = []
        for s in self.servers:
            if s != server and all(s != neighbor[0] for neighbor in server.get_neighbours()):
                servers.append(s)

        return servers

    def __establish_connection(self, server, x, y):
        available_servers = self.__get_available_servers(server)

        def validate(form_controls):
            index = form_controls["Serveurs disponibles"].current()
            if index == -1:
                raise ValueError("Veuillez sélectionner un serveur")

            neighbour = available_servers[index]
            server.add_neighbour(neighbour, form_controls["Temps de réponse"].get(), self.__canvas)

        (FormGenerator(self.__window, x, y, "Liaison de serveurs", [
            ("Temps de réponse", "entry"),
            ("Serveurs disponibles", "combobox")
        ])
         .build_form(validate, combobox_options=[s.ip_address for s in available_servers]))

    def __mark_as_research_starting_point(self, server):
        self.__research_starting_point = server

    def run(self):
        self.__window.mainloop()
