--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3 (Debian 15.3-1.pgdg120+1)
-- Dumped by pg_dump version 15.3

-- Started on 2023-08-02 08:26:34 UTC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 214 (class 1259 OID 16395)
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id_img integer NOT NULL,
    link_img text NOT NULL,
    date date NOT NULL
);


ALTER TABLE public.images OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16402)
-- Name: stones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stones (
    id_stone integer NOT NULL,
    id_img integer NOT NULL,
    boxes_conf text NOT NULL,
    boxes_xywh text NOT NULL
);


ALTER TABLE public.stones OWNER TO postgres;

--
-- TOC entry 3203 (class 2606 OID 16401)
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id_img);


--
-- TOC entry 3206 (class 2606 OID 16408)
-- Name: stones stones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stones
    ADD CONSTRAINT stones_pkey PRIMARY KEY (id_stone);


--
-- TOC entry 3204 (class 1259 OID 16414)
-- Name: fki_m; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_m ON public.stones USING btree (id_img);


--
-- TOC entry 3207 (class 2606 OID 16409)
-- Name: stones img_key; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stones
    ADD CONSTRAINT img_key FOREIGN KEY (id_img) REFERENCES public.images(id_img);


--
-- TOC entry 3355 (class 0 OID 0)
-- Dependencies: 3207
-- Name: CONSTRAINT img_key ON stones; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT img_key ON public.stones IS 'id_img будет связан с таблицей «images» отношением один ко многим';


-- Completed on 2023-08-02 08:26:34 UTC

--
-- PostgreSQL database dump complete
--

