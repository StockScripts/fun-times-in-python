-- Table: public.fact_fred_releases

-- DROP TABLE public.fact_fred_releases;

CREATE TABLE public.fact_fred_releases
(
  release_id numeric,
  link text,
  name text,
  press_release text,
  realtime_end date,
  realtime_start date,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  source_id numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.fact_fred_releases
  OWNER TO postgres;