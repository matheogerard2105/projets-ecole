DELETE FROM LIENS_GROUPES;
DELETE FROM GROUPE;
DELETE FROM LIEN_ADE;

INSERT INTO LIEN_ADE(LIEN) VALUES
('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/wpn8o5Y8.shu'),
('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/76YPd1Yv.shu'),
('https://planning-gestionnaire-2026.univ-lille.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=257fcd64e84c3542dfe30932400e8e96305be6e9b6eabac62489819354308d0fc168a35e4a76603dbc57d9ad5744b0a1dc5c094f7d1a811b903031bde802c7f515fb432d071eba001190cf5b00e256f9778691c2f3a694ea0a25af2f82d3f997f77e78ccad12ca897793c37046849caf14dbb816ef81af92dda366001d1ba81f,1')
,
('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/rY64RgWz.shu'),
('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/rv3VZj3b.shu');

INSERT INTO GROUPE(NOM) VALUES
('IS'),
('IS3'),
('IS2A3'),
('IS5'),
('IS2A4');

UPDATE GROUPE SET IS_SUPER_GROUP = true WHERE NOM='IS';

INSERT INTO SALLE(NUM, BATIMENT, TYPE_SALLE) VALUES
('310','B','TD'),
('311','B','TD'),
('313','B','TD'),
('112','B','TP'),
('115','B','TP'),
('113','B','TP'),
('204','A','TD');

INSERT INTO ENSEIGNANT(NOM) VALUES
('KESSACI MARIE-ELEONORE'),
('DESOMBRE MARTIN'),
('JANOT STEPHANE'),
('LEPERS MATHILDE'),
('GIRARD MATHILDE'),
('SEYNHAEVE FRANCK');

/* INSERTIONS DES LIENS DE CLES ETRANGERES */

/*************************

    FONCTIONS DE RÉCUP ID

**************************/

CREATE OR REPLACE FUNCTION get_groupe_id(p_nom VARCHAR)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    r_id INT;
BEGIN
    SELECT id INTO r_id FROM groupe WHERE nom = p_nom LIMIT 1;
    RETURN r_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_salle_id(p_nom VARCHAR)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    r_id INT;
BEGIN
    SELECT id INTO r_id FROM salle WHERE concat(batiment, num) = p_nom LIMIT 1;
    RETURN r_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_lien_id(p_lien VARCHAR)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    r_id INT;
BEGIN
    SELECT id INTO r_id FROM lien_ade WHERE lien = p_lien LIMIT 1;
    RETURN r_id;
END;
$$;

INSERT INTO LIENS_GROUPES(GROUPE_ID,LIEN_ID) VALUES
(get_groupe_id('IS'),get_lien_id('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/wpn8o5Y8.shu')),
(get_groupe_id('IS3'),get_lien_id('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/wpn8o5Y8.shu')),
(get_groupe_id('IS'),get_lien_id('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/76YPd1Yv.shu')),
(get_groupe_id('IS2A3'),get_lien_id('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/76YPd1Yv.shu')),
(get_groupe_id('IS'),get_lien_id('https://planning-gestionnaire-2026.univ-lille.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=257fcd64e84c3542dfe30932400e8e96305be6e9b6eabac62489819354308d0fc168a35e4a76603dbc57d9ad5744b0a1dc5c094f7d1a811b903031bde802c7f515fb432d071eba001190cf5b00e256f9778691c2f3a694ea0a25af2f82d3f997f77e78ccad12ca897793c37046849caf14dbb816ef81af92dda366001d1ba81f,1')
),
(get_groupe_id('IS5'),get_lien_id('https://planning-gestionnaire-2026.univ-lille.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=257fcd64e84c3542dfe30932400e8e96305be6e9b6eabac62489819354308d0fc168a35e4a76603dbc57d9ad5744b0a1dc5c094f7d1a811b903031bde802c7f515fb432d071eba001190cf5b00e256f9778691c2f3a694ea0a25af2f82d3f997f77e78ccad12ca897793c37046849caf14dbb816ef81af92dda366001d1ba81f,1')
),
(get_groupe_id('IS2A4'),get_lien_id('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/rv3VZj3b.shu'));

INSERT INTO LIENS_SALLES(SALLE_ID, LIEN_ID) VALUES 
(get_salle_id('A201'), get_lien_id('https://planning-2026.univ-lille.fr/jsp/custom/modules/plannings/rY64RgWz.shu'));





