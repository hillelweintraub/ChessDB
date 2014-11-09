CREATE DATABASE IF NOT EXISTS ChessDB;

USE ChessDB;

CREATE TABLE IF NOT EXISTS Users ( uuid      INTEGER AUTO_INCREMENT,
                                   username  VARCHAR(20) NOT NULL,
                                   password  VARCHAR(20) NOT NULL,
                                   email     VARCHAR(50),
                                   PRIMARY KEY (uuid),
                                   UNIQUE (username)
                                 );


CREATE TABLE IF NOT EXISTS Owned_Collections ( cid                 INTEGER AUTO_INCREMENT,
                                               cname               VARCHAR(50) NOT NULL,
                                               uuid                INTEGER NOT NULL,
                                               description         VARCHAR(150),
                                               tag                 VARCHAR(20),
                                               date_last_modified  TIMESTAMP NOT NULL,
                                               PRIMARY KEY (cid),
                                               UNIQUE (cname, uuid),
                                               FOREIGN KEY (uuid) REFERENCES Users
                                                       ON DELETE CASCADE 
                               );


CREATE TABLE IF NOT EXISTS Games ( gid                   INTEGER AUTO_INCREMENT,
                                   event_site            VARCHAR(50),
                                   event_name            VARCHAR(50),   
                                   event_round           REAL,
                                   date                  DATE,
                                   white_player_name     VARCHAR(30) NOT NULL,
                                   black_player_name     VARCHAR(30) NOT NULL,
                                   white_title           VARCHAR(5),
                                   black_title           VARCHAR(5),
                                   white_player_rating   INTEGER,  
                                   black_player_rating   INTEGER, 
                                   result                VARCHAR(7) NOT NULL,
                                   ECO_code              VARCHAR(5), 
                                   opening               VARCHAR(50),
                                   variation             VARCHAR(50),
                                   number_of_moves       INTEGER NOT NULL,
                                   move_list             VARCHAR(1000) NOT NULL,
                                   game_source           VARCHAR(20) NOT NULL,
                                   PRIMARY KEY (gid),
                                   UNIQUE (white_player_name, black_player_name, event_name,
                                           event_round, event_date)
                                 );


CREATE TABLE IF NOT EXISTS Contained_Games ( cid   INTEGER,
                                             gid   INTEGER,
                                             label VARCHAR(80),
                                             PRIMARY KEY (cid, gid),
                                             FOREIGN KEY (cid) REFERENCES Owned_Collections
                                                     ON DELETE CASCADE,       
                                             FOREIGN KEY (gid) REFERENCES Games
                                           );


CREATE TABLE IF NOT EXISTS Played_Moves ( mid             INTEGER AUTO_INCREMENT,
                                          prior_position  VARCHAR(80) NOT NULL,
                                          current_move    VARCHAR(5) NOT NULL,
                                          PRIMARY KEY (mid),
                                          UNIQUE (prior_position, current_move)
                                        );        


CREATE TABLE IF NOT EXISTS Contained_Moves ( gid INTEGER,
                                             mid INTEGER,
                                             PRIMARY KEY (gid, mid),
                                             FOREIGN KEY (gid) REFERENCES Games,
                                             FOREIGN KEY (mid) REFERENCES Played_Moves
                                           );