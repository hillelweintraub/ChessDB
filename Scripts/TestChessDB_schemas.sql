CREATE DATABASE IF NOT EXISTS TestChessDB;

USE TestChessDB;

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
                                               date_last_modified  TIMESTAMP NOT NULL
                                                                             DEFAULT CURRENT_TIMESTAMP
                                                                             ON UPDATE CURRENT_TIMESTAMP,
                                               PRIMARY KEY (cid),
                                               UNIQUE (cname, uuid),
                                               FOREIGN KEY (uuid) REFERENCES Users(uuid)
                                                       ON DELETE CASCADE 
                               );


CREATE TABLE IF NOT EXISTS Games ( gid                   INTEGER AUTO_INCREMENT,
                                   Site                  VARCHAR(50),
                                   Event                 VARCHAR(50),   
                                   Round                 REAL,
                                   Date                  DATE,
                                   White                 VARCHAR(30) NOT NULL,
                                   Black                 VARCHAR(30) NOT NULL,
                                   WhiteTitle            VARCHAR(5),
                                   BlackTitle            VARCHAR(5),
                                   WhiteElo              INTEGER,  
                                   BlackElo              INTEGER, 
                                   Result                VARCHAR(7) NOT NULL,
                                   ECO                   VARCHAR(5), 
                                   Opening               VARCHAR(50),
                                   Variation             VARCHAR(50),
                                   number_of_moves       INTEGER NOT NULL,
                                   move_list             VARCHAR(3000) NOT NULL,
                                   game_source           VARCHAR(20) NOT NULL,
                                   PRIMARY KEY (gid),
                                   UNIQUE (White, Black, Event, Round, Date)
                                 );


CREATE TABLE IF NOT EXISTS Contained_Games ( cid   INTEGER,
                                             gid   INTEGER,
                                             label VARCHAR(80),
                                             PRIMARY KEY (cid, gid),
                                             FOREIGN KEY (cid) REFERENCES Owned_Collections(cid)
                                                     ON DELETE CASCADE,       
                                             FOREIGN KEY (gid) REFERENCES Games(gid)
                                           );


CREATE TABLE IF NOT EXISTS Played_Moves ( mid             INTEGER AUTO_INCREMENT,
                                          prior_position  VARCHAR(80) NOT NULL,
                                          current_move    VARCHAR(10) NOT NULL,
                                          PRIMARY KEY (mid),
                                          UNIQUE (prior_position, current_move)
                                        );        


CREATE TABLE IF NOT EXISTS Contained_Moves ( gid INTEGER,
                                             mid INTEGER,
                                             PRIMARY KEY (gid, mid),
                                             FOREIGN KEY (gid) REFERENCES Games(gid)
                                                     ON DELETE CASCADE,
                                             FOREIGN KEY (mid) REFERENCES Played_Moves(mid)
                                                     ON DELETE CASCADE
                                           );
