import re


def replace_color_in_text(text: str, old_color: str, new_color: str):
    return text.replace(old_color, new_color)


def swap_color_in_text(text: str, color_1: str, color_2: str):
    temp_placeholder = "__TEMP__"
    text = replace_color_in_text(text, color_1, temp_placeholder)
    text = replace_color_in_text(text, color_2, color_1)
    text = replace_color_in_text(text, temp_placeholder, color_2)
    return text


def create_kickback(pregunta_in, respuesta_in):
    # Define the font style and size
    op_b = r"""{"""
    cl_b = r"""}"""
    question_style = r"""\\fnComic Sans MS\\u1"""
    normal_style = r"""\\fnAria\\u0"""
    yellow = r"""\\c&H00FFFF&"""
    white = r"""\\c&HFFFFFF&"""

    pregunta_out = re.sub(yellow, yellow + question_style, pregunta_in)
    pregunta_out = re.sub(op_b + white, r"\\N\\N\\N\\N" + op_b + white, pregunta_out) + r"\N\N\N\N\N"

    list_ask = re.split(r"\\N\\N", pregunta_out)
    list_res = re.split(r"\\N\\N", respuesta_in)

    respuesta_out = (list_ask[0] + re.sub(yellow + cl_b, normal_style + cl_b + r"\\N", list_res[0])).rstrip(
        op_b + white + cl_b)
    respuesta_out += (re.sub(cl_b, question_style + cl_b, list_ask[1]) +
                      r"\N\N" + list_ask[2] + re.sub(white, normal_style, list_ask[1]) + r"\N" + list_res[1])

    return pregunta_out, respuesta_out


if __name__ == '__main__':
    # Example usage:
    Texto = r"""Mira como me dicen que soy el Mauri. A pensas una mordida al micro y alucinas como brownie.
Mi hermano ya te apegas a los wawis.\NMe voy con cuatro anillos, parezco un Audi.
Yo tengo más troféos, man yo tengo más tornéos.
¡Vamos para el banco a ver quien tiene más dinero\Ny vamos pa la calle a ver quien es el más rapero!
¿No te das cuenta?
Mi hermano, este ya se ausenta.
El Hip Hop de cumpleaños cincuenta,\Nno va a ganar alguien que no lo representa.
Mi hermano, se repiten tus traumas del pasado.
¿Que no ves lo que ha pasado?\NTe gana el moreno con un boricua en el jurado.
Segundón
Maldito maricón,
maldito llorón, ¡tienes todo menos algo y eso es casta de campeón!
El mejor del mundo, el que tiene el éxito profundo, el éxito rotundo.\NTú paras el tiempo, eres un eterno segundo.
Hey que sencillo te doy un palizón.\NClaro que lo humillo en la competición.
Este pardillo es un mojón.\N¡Se va con cuatro anillos y yo con un cinturón!
Me lo cargo, ¿ves? Conmigo no tienes nada que hacer, no me impresiona.\NTus FMS tampoco tus coronas. ¡Te humillo como rapero, te mato como persona!
En tres dos uno, sé que lo parto en este momento.\N¿Sobre orquesta? la verdad que me toca este gil.\N
Hoy no me hace falta arco porque lo voy a partir\Ny no te acerques a mi hermana que sé que sos un violín.
Le falta, mano al aire, ven lo que le falta. Maturin rapea tranqui, no se rompe la garganta\Npero para rapear me dejo el alma porque para ser parte de mi orquesta a vos te falta una banda.
A mí no me falta una banda, porque las personas siempre mantienen su orquesta en el alma y en su mente.\NLas personas como tú deberían de estar en el parque. ¡Ojalá yo ser Beethoven solo para no escucharte!
Yo estoy en el parque, el parque está en mi corazón, porque la gente de parque siempre me da la razón.\NMi voz es un instrumento de viento en esta actuación, ¡y mis manos en tu pecho son otros de percusión!
Son otros de percusión, pero tú rapeas por dinero, por la fama y por la repercusión.\NSabemos que no tienes cosas claras. ¿Cómo le ponen orquesta al de la tierra de Mozart La Para?
No no no me dice nada, todo el mundo sabe bien que va a ganar Maturín, porque tiene buenas rimas.\NHoy va a ganar el tipo de Argentina. Me siento director de orquesta. ¡Muevo las barras arriba!
Tú no eres la cura, de hecho no puedes fluir.\NManos arriba a toda la gente, los que me quieren oír.
El se queda en el rap, no puede fluir aquí.\NCojo como Dr. House, rapper como Dr. Dree.
No hermano lo voy a rapear y mirenlo ahora. Le estoy poniendo punto final, también dejando en coma.\NEste rapero es todo incierto, empezó entre comillas y termina entre camillas muerto.
¡Ey! ¡Let's go! Me dicen Brasil, yo lo quito. Qué mal rapea el favorito.\NÉl rapea cuadradito y Alemania hoy pierde contra el joga bonito.
A ti nadie te quiere escuchar, quieren otra ronda pa poderme apreciar.\NQue se quite y salga Aczino pa acá. ¡Diganle a Pelé que Messi vino por su mundial!
Lo ha querido intentar. A he-cho un a-rran-que a-sí pe-ro en-ver-dad le ha sa-li-do ya muy mal.\NEso es lo que pasa, me quiere imitar. ¡Luis Paquetá nunca jugará como Neymar!
Qué retraso tan mental. ¿Qué tiene que ver si yo tuve que emigrar?\NSi no emigro de mi país, probablemente caía preso. Pero eres de Costa Rica, ¿qué coño sabrás de eso?
Yo soy de Costa Rica, ¿y piensa que eso a mí me mortifica?\NYo vengo de un país de pobreza como el tuyo. Él lo esconde por vergüenza, yo lo grito por orgullo.
¿Quieres hablarme a mi de las banderas? No hablés de Colombia, hermano no tienes actitud. Pregunta en FMS, los conozco más que tú
Él los conoce, es pendejo y habla de ellos porque tiene reflejos.\NYo los conozco, no me acomplejo. Chupando tan bonito, cualquiera llega lejos.
Así que no cometas ese error. Mi gente en mi casa me ama y me entrega valor.\NMi hijo también me abraza y me da todo su amor. No me importa lo que voten, ¡yo ya soy un ganador!
¿Estando en La Nevera?\Nmás bien estando tan muerto, que va a perder en el evento.
Representa a USA, ¿es cierto?\N¡No me va a ganar quien tiene una bandera de repuesto!
Soy argentino, guacho, cuando rimo, yo te liquido.
Mi logro es ser campeón argentino.\NLo mejor que hiciste vos acá fue jugar play con Asesino.
Por favor, este tipo no es hombre,\Nél también jugó play. No digas nombres.
¿qué tengo una bandera de respuesta, hombre?\N¡Por eso lo que hago, aquí vale doble!
¿Qué vas a decir, hermano? Delante, el rap más gigante.
¿Como me habla de Estados Unidos este insignificante?\N¡Yo soy campeón mundial, siendo un inmigrante!
Les está tirando chamuyo, yo de la pista nunca huyo.
¿Representás a Estados Unidos con orgullo?\N¡el país que representás está matando el país tuyo!
¿Por qué, qué pasa en Venezuela?\NNo tienen educación, no tienen escuela.
No tienen nada hijo de perra.\N¡Me paso por la punta de la verga tu bandera!
Tres, dos, uno, tiempo. Con el nazo, mano por tu lado paso.\NA llegado tu reemplazo.
Loco sabes que yo te hago mierda.\NLlevas una L porque hoy te gana Leiva.
Yo te escupo flavor. Todo el mundo entiende de mi jerga.\NSoy el que está matando a la puta leyenda.
 Mira como con el Aczino termino. Él no rapea como yo rimo.
Él no rapea como yo rimo, primo. Si yo me avecino, conquisto a tus vecinos.\NMira qué es lo que te duele, mi niño. Si traigo una L, y está en las manos de asesino.
Bram! para la primera compa. Mira cómo ahorita le doy la derrota.\NDice que es mi reemplazo el Jota. Eres el reemplazo del Papo, es mi nueva mascota.
¿Timón y Pumba mi hermano? Lo siento parece que al fracaso ya estás anclado.\NOye, yo parezco un mago para los raperos. Miren el conejito que saqué bajo el sombrero.
Era ocho, no seas idiota.Te equivocaste otra vez, ¡imbécil de nuevo me toca!\NPorque tú sabes que dejo claro. Te prestaré esta brújula porque no sabes donde estás parado.
No sabes rapear ni menos, estando aquí arriba. Tomó esto para manejar el barco en la tarima. Quiere manejar un barco y no maneja ni su vida.
Hijo de puta te rapeo, tengo más habilidad y eso es lo que creo.
Mi hermano, me ponen en un pájaro contra mi contrincante.\NRed Bull no me dió alas, ¡yo volaba desde antes!
Lo mato y lo destripo, mi flow yo se lo indico.\NLo voy a sacar a este y a todo su equipo.
Ahora miras triple, te lo explico papito,\Nes un encuentro cercano pero es del tercer tipo.
Si, tiene razón, sus rimas son muy secundarias.\NLe voy a enseñar a usar la materia primaria.
Es 51, está hablando del área,\Npues la cara del Diego ahora es mi Vía Lactea.
No lo entiende, hago que borre. Yoiker si es todo un cabrón, van a ver como aste ahora corre.\NMe toca matar y asesinar a Diego Flores, pero no soy un patán, a Diego le mando flores.
Él ganó God Level con Marithea, desde chico,\No sea que pa ganar necesita un colombiano en tu equipo.
Claro que hermano, Marithea, Valles-T, Carpe te lo han logrado\Ny ahora quieres el cinturón, mano. Quieres recoger un campo que tú no has cosechado.
Porque tan solo eres escoria. Dices frases de mi trayectoria.\NYo soy el artista, tú el escritor que cuenta mi historia. Yo vivo del arte y tú de la memoria.
{\pos(6900,4297.5)}¿Qué ha pasado? Solo eres un retrasado. La felpa que te acabo de dar.\NSoy un vendedor ambulante porque te sirvo en cualquier lugar.
Hey loco, co-co-co-co-como la desmonto.\NCo-co-combo, combo tras combo.
Ahora yo voy al gimnasio, pero tonto.\N¡Estoy mucho más en forma, pero rapeo más gordo!
"En el gimnasio." Tarado,\Neste man nunca me ha ganado.
Parece un abdomen de un físico culturista entrenado,\N¿saben por qué?, porque rapea cuadrado.
Rapeo cuadrado, de verdad es la historia,\Nporque tengo trayectoria.
¿No hablabas de la selección escoria?\N¡Soy Cuadrado porque soy un capitán para Colombia!
"Entrenan la garganta", perro.\NYo le gano y siempre me alegro.
Abdominales de corazón hago y te desintegro.\NY aquí las flexiones se hacen con el cerebro.
¿Tú no entiendes? Este rapper para mí es un incoherente. Se dejó lastimar por lengua y le tumbé todos los dientes. Recuerda que la lengua es el músculo más fuerte.
¡Hey! ¡hey! Yo tengo más nivel, yo le voy a ganar, hago un mejor papel. El va al gimnasio todo los días este man. Gazir por más que entrenes piernas ¡nunca vas a crecer!
Cerrá bien el orto la concha de tu hermana, porque a mi no me duele, él no me dice nada.
Miren el truco que le hago en la cara. ¡Diganme quien de los dos puso más alta la vara!
No me gana, bro. Ya sabes que yo soy el mejor. Por eso ya te gano. ¿Y es que qué me va a decir? El genio frota la lámpara para verme a mi.
No me dice nada el brother. Lo que este me dice no me jode. Argentina va a sacar a los españoles. Así que, Chuty, vení, vení. ¡Óle!
Sí, sí. ¡Olé! Hermanito, lo que hago es rápido. Le ganó a Aczino porque hizo un pacto satánico y Skone de jurado es su nuevo padrino mágico.
Tú ya me la chupas, te noquéo. Me dices óle, eso es lo que veo. Por su puesto porque en el torneo el español va a ganar los toros, no le den más rodeos.
No, no, no. No, no, no. Cerrá el orto, topo. Nada de racismo, yo con eso no me topo.
Tiene una lámpara de oro, ¿lo vieron a este topo? Sus lámparas son de oro que nos roban a nosotros.
Hey, como un gran faraón. Yo domino los mares como Poseidón, tú eres pose y ¿dónde dejaste tu talento? Tú eres un dios pero estoy en crecimiento.
Tú estás en crecimiento, a mi me hacen monumentos, cada vez que tomo el micrófono y te lo reviento.
Mi hermano. ¿Sabes lo que hago?, yo te paso. Te dejo a cuatro patas y vuelas como pegaso.
Como pegaso, abro las alas, por ti yo paso. Mano sabes que despedazo. Tú no eres el Diablo, ¿entiendes lo que hablo? Soy un animal, minotauro.
Minitauro, más bien mini Mauro porque caundo llego a todos los desarmo.
¿Sabes qué pasa? Te hago bailar dansón. No jueges con las patadas a Sansón
Va a perder hoy en día, pero mi nombre va a quedar escrito en la mitología. Así que la mente abran. Yo podría entrenar a Hércules porque soy una cabra.
Por esa razón yo ahora le gano a este hermano. Él siempre presume su nacionalidad temprano.
Es de USA, pero dice ser cubano. Y un sueldo de USA alimenta a 40 colombianos.
Mano, te espero. Yo sí que te gano, rapero. Tú no eres del tercer mundo. Tú no eres un buen rapero. Vendiste tu tercer mundo para comprar el primero.
Te lo juro que allá hay más, sino que la gente siempre prefiere confiar. Eso hubiera pasado si yo no hubiera estado acá pero estoy callando las bocas que antes solían hablar.
Eso es lo que hace mi rap, lo que hace mi verso y lo que hace mi calidad.
Este evento me lo gano por usted y por mi mamá y por la gente que está escuchando y siempre tendió a confiar.
Primero que nada bendiciones para Colombia, shout-out para las comunas y amor para el que me odia.
Este tipo nunca tuvo vida propia. Hablando mucho de mi vida eres igualito a mi exnovia.
Él es colombiano el tipo si que es de barrio, por eso a colombia quería representarlo pero tu no eres Marithea, para serlo te faltaron ovarios. Así que calla.
Lo que cueste. Yoo puedo ser cubano americano hasta diciembre, que pase lo que pase seguiré siendo Reverse y el gane lo que gane nunca va a ser Valles-T.
De antes, los cubanos somos representantes y hacemos chistes para los grandes y Colombia que está triste porque se fue el comediante.
Como la clavo mi hermano, vengo desde el sur hasta el norte. Pa que la gente se sepa que yo lo voy a matar con este acote.
Sonicko tírame un corte. No vas a ganar ni aunque baje un arcángel y lo convenza al Arcángel para que te vote. ¡Oh shit!
De que te vote mi hermano. Creo que voy yo, quedate callado.
Porque no estás preparado. A ver, párate de manos. Los que sabemos de hip-hop por la pantalla no nos guiamos.
El corazón nos dice mandale entonces le mandamos.
Así es que te voy a decir. ¿Y ahora me está haciendo caras a mi? ¿Te preocupa? Mi estilo te mata por perra y también te ejecuta.
Y habló de Arcángel, se puso como una groupie o como una puta. ¿Vas a votar por el que rapea o por el que mate la chupa?
Yo lo elimino, creo elimino, no puede el flow capitalino. Yo lo combino, yo lo combino, saco flow si lo patrocino.
Yo vengo de dólar, te explico padrino, no me puede hacer nada el peso de un argentino.
Pero te espera un asado cuando regreses cordobés.
Nada que ver lo que dijo. Las manos al aire que saben que yo acá lo tengo de hijo, fijo. Porque saben bien que como un argentino lo piso.
Yo se muy bien hacer los asados, por eso los hago prolijo. El Yoiker llega temprano ¡porque quiere probar el chorizo!
Yoiker, Yoiker yo te gano en esta ronda madafaca. Por eso se que te gano y te juro que acá te reviento.
¿Qué el peso argentino es menos que el dólar? lo sé pero lo siento. ¡Y nunca subestimes a un argentino hambriento!
Yo soy argentino y vos sos mexicano, eso es cierto. Sos del país donde se hizo el último evento. Y me chiflaron, y vos no hiciste nada al respecto sabiendo que si das al revés, soy el primero en hacerlo.
¡Cara de verga! Por eso perdés cada compe. Tu nivel no llega a ligas, tu nivel nunca la rompe. ¿Saben por qué en México nadie lo quiere este torpe? Porque tiene el ego de Aczino y el nivel de Yoiker.
¡Que se calle la boca, se calle la boca! Manos arriba de toda la tropa. ¿El argento viene a hambriento? Eso no me incomoda y para que vean que soy bueno te la puedes comer toda.
Le pego hasta que se muera, sueno tan cabrón que parece una balacera.
¿Cómo ven? Protesta mucho el rey, pero al rato en tres años, un spot para Milei.
¿No lo entienden? Se quiebra. Lo voy a matar. Le levanto las sospechas.
¡Pobre! Que ya se nos fue el maldito Mecha. Me parezco a Milei, lo tumbe con la derecha.
No me gana este rapero, porque honor tiene cero.
El año pasado, mierda de rapero, ¡sonreías mientras que pisaban a todos tus compañeros!
¿Qué me va a contar, man? No tiene nada que hacer.
La mala persona que bajó el nivel, actúa como Maradona y ya no juega como él.
Con competidores, con competiciones, a los seguidores, criticas todo mi brother, eres el único que caga en el mismo plato que come
Dime hermano. Por supuesto que te gano. Tus esfuerzos serán en vano, por todos los asesinos rinden cuentas con Dios tarde o temprano.
El más rapero llegó, soy Mau el Aczino. Yo soy el mejor que se ha parido. Tú eres Chuty mi amigo, ¡y tu máximo logro es que te comparen conmigo!
Es exceso de talento, tú exceso de entrenamiento. ¿El mejor cuando el freestyle está muerto? ¡Yo el mejor en su mejor momento!
Yo no soy obvio, le gano sobrio, la gente sonrió cuando vio que el que está soy yo. ¿Cómo no?, cómodo, hey youh. La molotov explotó. Me merezco otro pódio y no la gano por Dios.
¡Ouh! Así se rapea con... con gente. Lo sabes bien hermano, soy de Córdoba. Pero hoy voy a explotar la pólvora. Bitches, Mitchell como Donovan. Me sentí en casa estándo en Bogotá.
El no está bien, el dice que es Don Omar, pero yo soy el que salió con su mujer.
¿Vieron que no puede y que no tiene nivel?. Qué te perdone Chuty, ¡yo no lo voy a hacer!
no que no era en tu país, y ahora que te está contando, está temblando Colombia como en los tiempos de Pablo.
En los tiempos de Pablo yo le gano rap real, por eso yo le gano esta manca. Reconocen estas voces en la santa, Colombia y Estados Unidos. Pablo en Casa Blanca.
Por eso en el beat tú te quitas, yo sí que le gano a este marica. Dije en la instrumental y en la salsa, qué palabras tan bonitas. La instrumental es la salsa que Colombia necesita.
El tipo se contradice en todo lo que dice. Goku contra Freezer. El narcotráfico arruina países. Apaga el televisor, Fat, no lo romantices.
"No lo romantices." Mano le gano en verdad. Yo si que le ganaré a este man.
Goku contra Freezer, eso si es verdad, porque siempre Freezer pierde contra Goku Black.
¿Rapear del futuro, cabrón?. Yo soy el mejor de la competición.
Yo soy Dragon Ball Z uno, en este patrón, ¡por qué me ganaré la saga sin ni una transformación!
Ahora mejor delira. Yo sé que le queréis ganar, pero eso no intimida. Antes me preocupaba si no me gritaban las rimas. Ahora soy una ruleta rusa, los vacíos me dan vida.
Aquí te gritan mucho porquería. Ve a España y dile a tu gente que algún día sea como la mía.
Él es el mejor freestyler de todos los tiempos. Lo que él se demoró tres años, yo lo hice en mi primer intento.
Ya, ya se acabó el evento. Por eso en el beat yo sí tengo más actitud. Se llama Nitro, ¿tú? Si es tan rápido, ¿por qué se demoró tanto para llegar a Red-Bull?
Me demoré pa llegar a Red Bull, te lo puedo explicar por si no sabes rapear.
Hermano me demoré, pero llegué al final. Ellos saben que todo lo bueno se hace esperar.
50 años del hip-hop, por eso los jodo, ¡pues yo tengo 17 y ya rapeo más que todos!
En el beat.\NVos no tenés el puesto.
¿Y qué hablamos de eso? Esta trenza que tenés también hace parte de mis ancestros.
¿Pero de qué se trata, compañero? No tiene habilidad, ni es sincero. Hermano te fijaste en mi pelo en la competencia. Fíjate en mi nivel, puto, no en mis apariencias.
Si lo que te importa para que tu lo vieras y siento. Te voy a matar al momento.
Te fijas en mi pinta, te fijas en mi aspecto. Por fijarte tanto en lo de afuera ¡te voy a romper por dentro!
En Colombia hay mucha calle, man. Pero en la calle le falta a este chaval.
Tú en la calle eres como un lector que no se quiere olvidar, hasta marca las esquinas pa saber por dónde va.
¿Ves cómo te gano?, esta es la hazaña. Chuty gana esta campaña.
Si mi país a ti tanto te daña. ¿Por qué pides el traspaso para FMS España?
No, no, no, no. Este raper es re mierda. Yo me fuí pa España para volverme leyenda, y para cobrar en euros, mi país está hecho mierda. Basicamente soy Cristobal Colón a la inversa.
No me ganas, te lo digo. Y sin gritar. ¿Me hablas sobre el Aczino? Nosotros hicimos el camino. Él es un secuestrado, tiene que imaginar el recorrido.
Me lo cargo. Yo soy el mejor de largo. Es un científico, yo un abuelo amigo. Tú lo has estudiado, ¡yo lo he vivido!
Las contrarresto, de un modo que suena modesto, menso. Man suena muy molesto.
Yo soy mejor actor que el resto, hice toda la escena teniendo el doble de riesgo.
Este chico me la chupa la verdad. De Latinoamérica me vino a contar. No compares a Colón conmigo. El oro que hoy me voy a llevar me lo da el pueblo latino.
De rehén hermano, yo a los eventos los siento. Y voy a las compes porque las represento.
Yo estoy en contra de los políticos hambrientos. Y sé que para ganarle hay que robarle desde adentro.
Ustedes la chuparon, vos y Aczino, los dos me la pelaron. Plantaron la semilla y está bastante claro. Pero empezá a respetarme que ¡nosotros las regamos!
Yo le voy a educar con rimas y aquí el racismo se termina. Tú tan mal no lo habrás pasado en la vida si criticas la tierra por culpa del hombre que la camina.
Tú eres un rapero que entra calidad. Lo siento mi hermano si rapeo y te parto a la mitad. Quiero manos arriba de todo Colombia si es que me van a escuchar, porque yo represento, hermano, incluso en la semifin
Ese rapero se cree bueno, no tiene calidad. Sabe que no es un estilo que me puede a mi ganar, porque para tener este flow, no tiene capacidad. La Mecha le tiene Nitro, le falta velocidad.
La verdad que no me gana, me porto re karateca. La gente me vió destacando ayer en nivel azteca. Lo saben porque el argentino siempre trae las letras. La verdad es que este putito a mí no me representa.
Tiene que meter un montón de relleno en todas sus rimas para rellenar una barra completa. No sé si estoy en Colombia o estoy en Venezuela, pero con ese relleno podría vender arepas.
A él le duele que vaya a rapear, que me ponga en otro país. Eso es lo que te duele pedazo de gil. El otro año voy a España pa romperte el culo a ti.
No vas a ir a España porque acá rapeaste mal. Vos no vas a ir a España, no llegaste a la final.
Es chileno y argentino, la historia te va muy mal. Porque acá me siento Messi. ¡Otro chileno sin mundial!
Mira a los compañeros que están en la grada y también al público, mírale a la cara. Todos saben que yo te ganaba. Ya estamos cansados de esta dictadura forzada.
Míralos, hermano, no todos son colombianos, también vinieron mexicanos, solo 300, pero somos espartanos.
¿Y qué más dan los países, amigo?, me quieren chilenos, argentinos, peruanos y todos los latinos. Mi cinturón es lo único que hace que todos estén unidos.
"Que todos estén unidos". Mira cómo viene resentido.
Mi hermano, es el Aczino. ¡Te faltan otros dos para compararte contigo!
Claro que yo te doy otro palizón. Contigo no hay comparación. Tú eres el tricampeón. ¡Yo solo con uno genero más ilusión!
¡Genera más ilusión, porque todo está en su imaginación!
Mi hermano tú no haces milagro. Hoy es tierra del diablo, como en tiempos de Pablo.
Te escondiste del lobo, bastardo Y en FMS tuve que esperarlo. Ese es un bastardo. ¡Si el diablo no sube hasta el cielo, bajo el infierno buscarlo!
Por eso le gano en efecto. Yo soy un freestyler perfecto. Él es el dios de los eventos. Y Dios se murió contra un humano, pues soy tu mejor invento.
Él es un gladiador maldito. Por eso en el beat yo sí le gano al pendejo.
Esto es Diamantes de Sangre y yo no me quejo, lo niños cogen las armas, recogen diamantes viejos.
Ya lo ves, qué cabrón. Me habla de los diamantes en la competición. Tú no tienes valor. ¡Confunden al diamante con piedras en el riñon!
Tú no tienes valor. Confunden al diamante con piedras en el riñón.
¿Tienes piedras en el riñon? Mano, yo sí que ya te voy a ganar, yo soy como Leonidas en este lugar. ¡Mi piedra en el riñon es la piedra filosofal!
El es Leonidas, dice, que escoria. Yo tengo 300 títulos en mi trayectoria.
Soy Messi, lo saben de memoria. Tengo mi mundial, ¡soy el mejor de la historia!"""

    text = Texto.replace("\\N", " ")

    print(text)
