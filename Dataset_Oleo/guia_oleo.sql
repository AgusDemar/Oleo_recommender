/* 
-- RATINGS

drop table if exists ratings;

create table ratings (
	id_usuario varchar(255),
	id_restaurante varchar(255),
	fecha varchar(255),
	comentario varchar(10000),
	rating_ambiente integer,
	rating_comida integer,
	rating_servicio integer,
	muy_util integer
);

copy ratings from 'C:/Users/Usuario/Documents/Maestria_DM/Sistema_de_recomendacion/Dataset_Oleo/ratings_train.csv' with csv header ENCODING 'ISO88591';

select * from ratings limit 300;

-- aca va la magia

copy (select id_usuario, id_restaurante, rating_ambiente from ratings) to 'C:/Users/Usuario/Documents/Maestria_DM/Sistema_de_recomendacion/output_oleo/ratings_ambiente.csv' with csv header ENCODING 'ISO88591';
*/

/*
-- USUARIOS
drop table if exists usuarios;

create table usuarios (
	id_usuario varchar(255),
	url varchar(255),
	nombre varchar(255),
	edad varchar(255),
	fecha_alta varchar(255),
	genero varchar(255),
	tipo varchar(255)
);

copy usuarios from 'C:\Users\Usuario\Documents\Maestria_DM\Sistema_de_recomendacion\Dataset_Oleo\usuarios.csv' with csv header ENCODING 'ISO88591';

select * from usuarios limit 100;

-- aca va la magia

copy (select id_usuario, edad, fecha_alta, genero, tipo from usuarios) to '/home/rabalde/Escritorio/guia_oleo/salida/usuarios.csv' with csv header ENCODING 'ISO88591';

*/


-- RESTAURANTES

drop table if exists restaurantes;

create table restaurantes (
	id_restaurante varchar(255),
	url varchar(255),
	nombre varchar(255),
	localidad varchar(255),
	cocina varchar(255),
	direccion varchar(255),
	telefono varchar(255),
	precio varchar(255),
	rating_comida varchar(255),
	rating_servicio varchar(255),
	rating_ambiente varchar(255),
	recomendado_para varchar(1000),
	latitud varchar(255),
	longitud varchar(255),
	reseña varchar(3000),
	horario varchar(2000),
	medios_pago varchar(255),
	caracteristicas varchar(255),
	fotos varchar(255),
	premios varchar(1000)
);

copy restaurantes from 'C:\Users\Usuario\Documents\Maestria_DM\Sistema_de_recomendacion\Dataset_Oleo\restaurantes.csv' with csv header ENCODING 'ISO88591';

select * from restaurantes limit 100;

-- medios_pago
select distinct medios_pago from restaurantes;

select trim(split_part(medios_pago,';',1)) from restaurantes union
select trim(split_part(medios_pago,';',2)) from restaurantes union
select trim(split_part(medios_pago,';',3)) from restaurantes union
select trim(split_part(medios_pago,';',4)) from restaurantes union
select trim(split_part(medios_pago,';',5)) from restaurantes union
select trim(split_part(medios_pago,';',6)) from restaurantes union
select trim(split_part(medios_pago,';',7)) from restaurantes;
/*
"Diners"
"Mastercard"
"Tarjeta Naranja"
"American Express"
"Maestro"
""
"Electrón"
"Cabal"
"Sólo Efectivo"
"Visa"
*/
-- aca va la magia

alter table restaurantes add column medios_pago_visa integer default 0;
update restaurantes set medios_pago_visa = 1 where medios_pago like '%Visa%';
alter table restaurantes add column medios_pago_master integer default 0;
update restaurantes set medios_pago_master = 1 where medios_pago like '%Mastercard%';
alter table restaurantes add column medios_pago_diners integer default 0;
update restaurantes set medios_pago_diners = 1 where medios_pago like '%Diners%';
alter table restaurantes add column medios_pago_naranja integer default 0;
update restaurantes set medios_pago_naranja = 1 where medios_pago like '%Naranja%';
alter table restaurantes add column medios_pago_american integer default 0;
update restaurantes set medios_pago_american = 1 where medios_pago like '%American%';
alter table restaurantes add column medios_pago_maestro integer default 0;
update restaurantes set medios_pago_maestro = 1 where medios_pago like '%Maestro%';
alter table restaurantes add column medios_pago_electron integer default 0;
update restaurantes set medios_pago_electron = 1 where medios_pago like '%Electr_n%';
alter table restaurantes add column medios_pago_cabal integer default 0;
update restaurantes set medios_pago_cabal = 1 where medios_pago like '%Cabal%';
alter table restaurantes add column medios_pago_efectivo integer default 0;
update restaurantes set medios_pago_efectivo = 1 where medios_pago like '%S_lo%Efectivo%';
alter table restaurantes add column medios_pago_nulo integer default 0;
update restaurantes set medios_pago_nulo = 1 where medios_pago like '' or medios_pago like ' ';
alter table restaurantes add column suma_medio_pago integer default 0;
update restaurantes set suma_medio_pago = medios_pago_visa + medios_pago_master + medios_pago_diners + medios_pago_naranja + medios_pago_american + medios_pago_maestro + medios_pago_electron + medios_pago_cabal + medios_pago_efectivo;

alter table restaurantes drop column medios_pago;

-- PREMIOS
alter table restaurantes add column cant_premios integer default 0;
update restaurantes set cant_premios = array_length(regexp_split_to_array(premios,';'),1);
update restaurantes  set cant_premios = 0 where cant_premios is null; 

-- RECOMENDADO_PARA
select trim(split_part(recomendado_para,';',1)) from restaurantes union
select trim(split_part(recomendado_para,';',2)) from restaurantes union
select trim(split_part(recomendado_para,';',3)) from restaurantes union
select trim(split_part(recomendado_para,';',4)) from restaurantes union
select trim(split_part(recomendado_para,';',5)) from restaurantes union
select trim(split_part(recomendado_para,';',6)) from restaurantes union
select trim(split_part(recomendado_para,';',7)) from restaurantes;
/*
Comer al aire libre 
Comer bien gastando poco 
Comer con buenos tragos 
Comer mucho 
Comer rápido 
Comer sano 
Comer sin ser visto 
Comer solo 
Comer tarde 
Escuchar música 
Ir con amigos 
Ir con chicos 
Ir con la familia 
Ir en pareja 
Llevar extranjeros 
Merendar 
Reunión de negocios 
Salida de amigas 
*/

alter table restaurantes add column ir_en_pareja integer default 0;
update restaurantes set ir_en_pareja = substring(recomendado_para from 'Ir en pareja \((\d+) votos\)')::int where recomendado_para like '%Ir en pareja%';
select recomendado_para, ir_en_pareja from restaurantes;
alter table restaurantes add column comer_aire_libre integer default 0;
update restaurantes set comer_aire_libre = substring(recomendado_para from 'Comer al aire libre \((\d+) votos\)')::int where recomendado_para like '%Comer al aire libre%';
select recomendado_para, comer_aire_libre from restaurantes;
alter table restaurantes add column gastando_poco integer default 0;
update restaurantes set gastando_poco = substring(recomendado_para from 'Comer bien gastando poco \((\d+) votos\)')::int where recomendado_para like '%Comer bien gastando poco%';
select recomendado_para, gastando_poco from restaurantes;
alter table restaurantes add column buenos_tragos integer default 0;
update restaurantes set buenos_tragos = substring(recomendado_para from 'Comer con buenos tragos \((\d+) votos\)')::int where recomendado_para like '%Comer con buenos tragos%';
select recomendado_para, buenos_tragos from restaurantes;
alter table restaurantes add column comer_mucho integer default 0;
update restaurantes set comer_mucho = substring(recomendado_para from 'Comer mucho \((\d+) votos\)')::int where recomendado_para like '%Comer mucho%';
select recomendado_para, comer_mucho from restaurantes;
alter table restaurantes add column comer_rapido integer default 0;
update restaurantes set comer_rapido = substring(recomendado_para from 'Comer rápido \((\d+) votos\)')::int where recomendado_para like '%Comer rápido%';
select recomendado_para, comer_rapido from restaurantes;
alter table restaurantes add column comer_sano integer default 0;
update restaurantes set comer_sano = substring(recomendado_para from 'Comer sano \((\d+) votos\)')::int where recomendado_para like '%Comer sano%';
select recomendado_para, comer_sano from restaurantes;
alter table restaurantes add column comer_sin_visto integer default 0;
update restaurantes set comer_sin_visto = substring(recomendado_para from 'Comer sin ser visto \((\d+) votos\)')::int where recomendado_para like '%Comer sin ser visto%';
select recomendado_para, comer_sin_visto from restaurantes;
alter table restaurantes add column comer_solo integer default 0;
update restaurantes set comer_solo = substring(recomendado_para from 'Comer solo \((\d+) votos\)')::int where recomendado_para like '%Comer solo%';
select recomendado_para, comer_solo from restaurantes;
alter table restaurantes add column comer_tarde integer default 0;
update restaurantes set comer_tarde = substring(recomendado_para from 'Comer tarde \((\d+) votos\)')::int where recomendado_para like '%Comer tarde%';
select recomendado_para, comer_tarde from restaurantes;
alter table restaurantes add column escuchar_musica integer default 0;
update restaurantes set escuchar_musica = substring(recomendado_para from 'Escuchar música \((\d+) votos\)')::int where recomendado_para like '%Escuchar música%';
select recomendado_para, escuchar_musica from restaurantes;
alter table restaurantes add column con_amigos integer default 0;
update restaurantes set con_amigos = substring(recomendado_para from 'Ir con amigos \((\d+) votos\)')::int where recomendado_para like '%Ir con amigos%';
select recomendado_para, con_amigos from restaurantes;
alter table restaurantes add column con_chicos integer default 0;
update restaurantes set con_chicos = substring(recomendado_para from 'Ir con chicos \((\d+) votos\)')::int where recomendado_para like '%Ir con chicos%';
select recomendado_para, con_chicos from restaurantes;
alter table restaurantes add column con_amigos integer default 0;
update restaurantes set con_amigos = substring(recomendado_para from 'Ir con amigos \((\d+) votos\)')::int where recomendado_para like '%Ir con amigos%';
select recomendado_para, con_amigos from restaurantes;
alter table restaurantes add column con_familia integer default 0;
update restaurantes set con_familia = substring(recomendado_para from 'Ir con la familia \((\d+) votos\)')::int where recomendado_para like '%Ir con la familia%';
select recomendado_para, con_familia from restaurantes;
alter table restaurantes add column llevar_extranjeros integer default 0;
update restaurantes set llevar_extranjeros = substring(recomendado_para from 'Llevar extranjeros \((\d+) votos\)')::int where recomendado_para like '%Llevar extranjeros%';
select recomendado_para, llevar_extranjeros from restaurantes;
alter table restaurantes add column merendar integer default 0;
update restaurantes set merendar = substring(recomendado_para from 'Merendar \((\d+) votos\)')::int where recomendado_para like '%Merendar%';
select recomendado_para, merendar from restaurantes;
alter table restaurantes add column reunion_negocios integer default 0;
update restaurantes set reunion_negocios = substring(recomendado_para from 'Reunión de negocios \((\d+) votos\)')::int where recomendado_para like '%Reunión de negocios%';
select recomendado_para, reunion_negocios from restaurantes;
alter table restaurantes add column salida_amigas integer default 0;
update restaurantes set salida_amigas = substring(recomendado_para from 'Salida de amigas \((\d+) votos\)')::int where recomendado_para like '%Salida de amigas%';
select recomendado_para, salida_amigas from restaurantes;
alter table restaurantes add column suma_votos integer default 0;
update restaurantes set suma_votos = ir_en_pareja + comer_aire_libre + gastando_poco + buenos_tragos + comer_mucho + comer_rapido + comer_sano + comer_sin_visto + 
				     comer_solo + comer_tarde + escuchar_musica + con_amigos + con_chicos + con_familia + llevar_extranjeros + merendar + reunion_negocios + salida_amigas;
select recomendado_para, suma_votos from restaurantes;


*/

-- TELEFONO

alter table restaurantes add column si_telefono integer default 0;
update restaurantes set si_telefono = case when telefono ~ '[0-9]+$' then 1 else 0 end;
select si_telefono from restaurantes 

select * from restaurantes;

copy restaurantes to '/home/rabalde/Escritorio/guia_oleo/salida/restaurantes.csv' with csv header ENCODING 'ISO88591';