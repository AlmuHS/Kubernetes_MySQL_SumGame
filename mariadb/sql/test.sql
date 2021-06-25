DROP DATABASE IF EXISTS GAMEDB;

CREATE TABLE IF NOT EXISTS JUGADORES(
    id int AUTO_INCREMENT,
    usuario varchar(20) UNIQUE NOT NULL,
    puntos_totales int,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS PARTIDAS(
        id int AUTO_INCREMENT,
        jugador int,
        fecha date,
        puntos int,
        PRIMARY KEY(id),
        FOREIGN KEY(jugador) REFERENCES JUGADORES(ID)
);
