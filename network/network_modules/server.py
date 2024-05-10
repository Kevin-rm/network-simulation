import re


class Server:
    half_side = 35
    __ip_address_pattern = re.compile(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    __sites_list_padding = 5
    __response_time_container_padding = 3

    def __init__(self, app, center_x, center_y, ip_address):
        self.__set_app(app)
        self.center_x = center_x
        self.center_y = center_y
        self.ip_address = ip_address

        self.__sites = []
        self.__neighbours = []  # Liste de Tuples contenant le serveur voisin et le temps de réponse(poids)
        self.__is_active = True  # Actif ou pas

        self.__tag = None  # Le rectangle qui représente le serveur sur le UI
        self.__ip_address_tag = None
        self.__sites_list_tag = None
        self.__line_tags = []

        # Pour le mécanisme de déplacement
        self.__start_x = None
        self.__start_y = None
        self.__is_moving = False

    def __set_app(self, app):
        from network_modules.app import Application

        if not isinstance(app, Application):
            raise TypeError("app doit être une instance de \"Application\"")

        self.__app = app

    @property
    def center_x(self):
        return self.__center_x

    @center_x.setter
    def center_x(self, center_x):
        if not isinstance(center_x, int):
            raise TypeError("center_x doit être de type \"int\"")

        if center_x < 0 or center_x > self.__app.window_width:
            raise ValueError("center_x doit être compris entre 0 et {}".format(self.__app.window_width))

        self.__center_x = center_x

    @property
    def center_y(self):
        return self.__center_y

    @center_y.setter
    def center_y(self, center_y):
        if not isinstance(center_y, int):
            raise TypeError("center_y doit être de type \"int\"")

        if center_y < 0 or center_y > self.__app.window_height:
            raise ValueError("center_y doit être compris entre 0 et {}".format(self.__app.window_height))

        self.__center_y = center_y

    @property
    def ip_address(self):
        return self.__ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        if not Server.__ip_address_pattern.match(ip_address):
            raise ValueError("L'adresse IP fournie \"{}\" est invalide".format(ip_address))

        self.__ip_address = ip_address.strip()

    @property
    def sites(self):
        return self.__sites

    @sites.setter
    def sites(self, sites):
        if not isinstance(sites, str):
            raise TypeError("L'argument sites doit être une chaîne de caractères")

        if not sites.strip():
            raise ValueError("La chaîne de sites ne peut pas être vide")

        for site in sites.split(";"):
            self.__sites.append(site.strip())

    def add_neighbour(self, neighbour, response_time, canvas):
        if not isinstance(neighbour, Server):
            raise TypeError("Le voisin d'un serveur doit être également un serveur")
        if not isinstance(response_time, str):
            raise TypeError("Le temps de réponse bien qu'il soit un entier doit être représenté sous forme de chaîne "
                            "de caratères")
        if not response_time.isdigit():
            raise TypeError("Le temps de réponse doit être un nombre entier")

        if neighbour in self.__neighbours:
            raise ValueError("Les deux serveurs sont déjà des voisins")

        response_time_int = int(response_time)
        if response_time_int <= 0:
            raise ValueError("Le temps de réponse ne peut pas être négatif ou nul")

        self.__neighbours.append((neighbour, response_time_int))
        neighbour.__neighbours.append((self, response_time_int))

        self.__draw_connection_line(canvas, neighbour, response_time_int)

    def get_neighbours(self):
        return self.__neighbours

    def start(self, canvas):
        self.__is_active = True
        canvas.itemconfig(self.__tag, fill="blue")

    def stop(self, canvas):
        self.__is_active = False
        canvas.itemconfig(self.__tag, fill="red")

    def is_active(self):
        return self.__is_active

    # Vérifie si des coordonnées (x, y) se chevauchent avec le serveur
    def is_within_bounds(self, x, y):
        return (self.center_x - Server.half_side <= x <= self.center_x + Server.half_side) and \
            (self.center_y - Server.half_side <= y <= self.center_y + Server.half_side)

    def __start_drag(self, event, canvas):
        self.__is_moving = True

        self.__delete_sites_list_tag(canvas)

        self.__start_x = event.x
        self.__start_y = event.y

        canvas.config(cursor='fleur')

    def __drag(self, event, canvas):
        if self.__is_moving:
            dx = event.x - self.__start_x
            dy = event.y - self.__start_y
            canvas.move(self.__tag, dx, dy)
            canvas.move(self.__ip_address_tag, dx, dy)

            for line_tag in self.__line_tags:
                l_tag, response_time_tag, background_tag = line_tag
                x1, y1, x2, y2 = canvas.coords(l_tag)
                if x1 == self.__center_x and y1 == self.__center_y:
                    canvas.coords(l_tag, x1 + dx, y1 + dy, x2, y2)
                else:
                    canvas.coords(l_tag, x1, y1, x2 + dx, y2 + dy)
                canvas.coords(response_time_tag, (x1 + x2) / 2, (y1 + y2) / 2)
                bbox = canvas.bbox(response_time_tag)
                canvas.coords(
                    background_tag,
                    bbox[0] - Server.__response_time_container_padding, bbox[1],
                    bbox[2] + Server.__response_time_container_padding, bbox[3]
                )

            self.__center_x += dx
            self.__center_y += dy

            self.__start_x = event.x
            self.__start_y = event.y

    def __stop_drag(self, canvas):
        self.__is_moving = False

        self.__start_x = None
        self.__start_y = None

        # Car losrqu'on arrête le dnd, on est directement en état de hover
        self.__start_hover(canvas)

    def __start_hover(self, canvas):
        if self.__is_moving is False:
            canvas.config(cursor='hand2')
            # Affichage de la liste des sites
            self.__create_sites_list_tag(canvas)

    def __stop_hover(self, canvas):
        if self.__is_moving is False:
            canvas.config(cursor='')
            self.__delete_sites_list_tag(canvas)

    def __bind_events(self, canvas, tag):
        # Lie les événements de survol au curseur
        canvas.tag_bind(tag, '<Enter>', lambda event: self.__start_hover(canvas))
        canvas.tag_bind(tag, '<Leave>', lambda event: self.__stop_hover(canvas))

        # Lie les événements de drag-and-drop
        canvas.tag_bind(tag, '<ButtonPress-1>', lambda event: self.__start_drag(event, canvas))
        canvas.tag_bind(tag, '<B1-Motion>', lambda event: self.__drag(event, canvas))
        canvas.tag_bind(tag, '<ButtonRelease-1>', lambda event: self.__stop_drag(canvas))

    def __create_sites_list_tag(self, canvas):
        if len(self.__sites) == 0:
            text = "Aucun site pour le moment"
        else:
            text = "Liste des sites :\n" + "\n".join(["- " + site for site in self.__sites])

        sites_tag = canvas.create_text(
            self.__center_x + Server.half_side + 10 + Server.__sites_list_padding,
            self.__center_y - Server.half_side + 15 + Server.__sites_list_padding,
            text=text,
            anchor='nw',
            fill="black"
        )
        bbox = canvas.bbox(sites_tag)
        background_tag = canvas.create_rectangle(
            bbox[0] - Server.__sites_list_padding,
            bbox[1] - Server.__sites_list_padding,
            bbox[2] + Server.__sites_list_padding,
            bbox[3] + Server.__sites_list_padding,
            fill="lightgrey",
            outline="gray"
        )
        canvas.tag_raise(sites_tag, background_tag)

        self.__sites_list_tag = (sites_tag, background_tag)

    def __delete_sites_list_tag(self, canvas):
        if self.__sites_list_tag is None:
            return

        (sites_tag, background_tag) = self.__sites_list_tag
        canvas.delete(background_tag)
        canvas.delete(sites_tag)
        self.__sites_list_tag = None

    def __draw_connection_line(self, canvas, neighbour, response_time):
        # La ligne entre les deux serveurs
        line_tag = canvas.create_line(self.__center_x, self.__center_y,
                                      neighbour.__center_x, neighbour.__center_y, width=1.5)
        # Affichage du temps de réponse au milieu de la ligne
        response_time_tag = canvas.create_text((self.__center_x + neighbour.__center_x) / 2,
                                               (self.__center_y + neighbour.__center_y) / 2,
                                               text=f"{response_time}", font=("Helvetica", 10, "bold"), fill="white")
        bbox = canvas.bbox(response_time_tag)
        background_tag = canvas.create_rectangle(bbox[0] - Server.__response_time_container_padding, bbox[1],
                                                 bbox[2] + Server.__response_time_container_padding, bbox[3],
                                                 fill="black", outline="white")

        self.__line_tags.append((line_tag, response_time_tag, background_tag))
        neighbour.__line_tags.append((line_tag, response_time_tag, background_tag))

        canvas.tag_raise(background_tag)
        canvas.tag_raise(response_time_tag)
        canvas.tag_raise(self.__tag)
        canvas.tag_raise(self.__ip_address_tag)
        canvas.tag_raise(neighbour.__tag)
        canvas.tag_raise(neighbour.__ip_address_tag)

    def reset(self, canvas):
        color = None
        if self.__is_active is True:
            color = "blue"
        else:
            color = "red"
        canvas.itemconfig(self.__tag, fill=f"{color}")

    def change_color(self, canvas):
        canvas.itemconfig(self.__tag, fill="green")

    def draw(self, canvas):
        from tkinter import Canvas

        if not isinstance(canvas, Canvas):
            raise TypeError("L'argument canvas doit être un objet de type Canvas du module tkinter")

        self.__tag = canvas.create_rectangle(
            self.__center_x - Server.half_side,
            self.__center_y - Server.half_side,
            self.__center_x + Server.half_side,
            self.__center_y + Server.half_side,
            fill="blue"
        )
        self.__ip_address_tag = canvas.create_text(
            self.__center_x,
            self.__center_y,
            text=self.__ip_address,
            fill="white"
        )

        self.__bind_events(canvas, self.__tag)
        self.__bind_events(canvas, self.__ip_address_tag)

    def __str__(self):
        return self.__ip_address
