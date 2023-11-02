import text_replacements
import dynamic_tags

def test_replacement(text, expected_result):
    actual_result = text_replacements.apply(text)
    actual_lines = actual_result.replace('\1', '‎').splitlines()
    expected_lines = expected_result.replace('\1', '‎').splitlines()
    
    lines_count = len(text.splitlines())

    for i in range(lines_count):
        if i < len(actual_lines):
            actual_line = actual_lines[i].lstrip()
        else:
            actual_line = ''

        if i < len(expected_lines):
            expected_line = expected_lines[i].lstrip()
        else:
            expected_line = ''

        length_delta = len(expected_line) - len(actual_line)
        
        if actual_line != expected_line:
            print('Test failed!')
            print(' > Actual  : ' + actual_line)
            print(' > Expected: ' + expected_line)
            if length_delta > 0: print('LENGTH DELTA: ' + str(length_delta))

            for i in range(min(len(actual_line), len(expected_line))):
                if actual_line[i] != expected_line[i]:
                    print('FIRST DIFFERENCE: ' + actual_line[i] + ' (char at index ' + str(i) + ')')
                    break

dynamic_tags.get('asasasa')
test_replacement("""100 de metri liber Campionatul Mondial de natație din Japonia
                    a CN Zaporijie
                    abc def / Analiză Kathimerini
                    Ambasada americană din Irak.
                    ambasadorul american la Bruxelles
                    Anglia. Poliția a arestat
                    Apple a lansat Apple Music Classical în Apple Music
                    Belarusului
                    București
                    Bulevardul Iuliu Maniu
                    bursa americană
                    cancelarul german la Cotroceni
                    Carpații Meridionali și de Curbură
                    Clujean dezgustat de condițiile de la Kaufland Mănăștur!
                    CN Zaporijia
                    Comandantul-șef al Armatei Ucrainene declară că războiul cu Rusia se îndreaptă către etapa pozițională, a luptelor de uzură, care ar putea aduce beneficii rușilor. Cere aliaților noi capacități și tehnologii-cheie, cu accent pe puterea aeriană de foc.
                    Comisia Juridică a Camerei Deputaților
                    Congresul american
                    conturilor Ministerului Finanțelor
                    de la Consiliul Europei
                    Europa caută să lupte împotriva valului de vehicule electrice chinezești, dar europenii le iubesc.
                    formațiune islamică
                    Guvernul german confirmă
                    Indo-Pacifică
                    în jurul parcării Operei ABCD
                    învățăturile Coranului sunt înțelepte
                    Maroc. Poliția declară
                    Marea Britanie. Poliția intensifică
                    Ministerul Rus al Apărării
                    ministrul israelian al apărării
                    occident\1ali afurisiți
                    Oceanul Atlantic, nu Oceanul Indian
                    Oceanul Atlantic de Nord
                    Pământul străbate un nor de praf lăsat de comenta Halley
                    Parchetul European
                    Pentru a ajunge pe Pământ.
                    Piețele europene avansează
                    Platforma X e nașpa
                    Președinta Comisiei Europene condamnă
                    Președinta Parlamentului European: deputații din Ucraina și Republica Moldova ar putea să primească statutul de observatori
                    Președintele bielorus i-a cerut ministrului rus al Apărării
                    Președintele Ecuadorului a cerut
                    Președintele Serbiei a dizolvat
                    președintele Taiwanului și cel al Camerei Reprezentanților
                    prezentate de armata israeliană
                    Primăria Craiova caută artiști
                    Reportaj The Guardian: Ambiția României pentru o nouă și vastă rezervație naturală, ca un ”Yellowstone al Europei”
                    Șeful Armatei Române
                    serviciile de informații rusești
                    serviciile speciale italiene
                    serviciul ucrainean de securitate
                    Serviciul Român de Informații
                    sistemele HIMARS, rachete
                    Statele Unite. Guvernul lansează
                    Steagul Franței
                    Studiu. “Semnele vitale” ale Pământului sunt tot mai slabe
                    SUA. Congresul
                    Târgu Mureș
                    Tokmak-Melitopol
                    Trafic blocat pe DN2, în aproprierea localității Traian
                    Urs semnalat în Râmnicu Vâlcea
                    WP: Unul dintre""",
                 """100 de metri liber 🏆#CampionatulMondialDeNatație din 🇯🇵#Japonia
                    a centralei nucleare ☢️#Zaporijie
                    Analiză 📰#Kathimerini: abc def
                    📜#AmbasadaAmericii din 🇮🇶#Irak.
                    📜#AmbasadorulAmericii la #Bruxelles
                    🏴󠁧󠁢󠁥󠁮󠁧󠁿#Anglia. 👮#PolițiaEngleză a arestat
                    🍏#Apple a lansat 🎵#AppleMusicClassical în 🎵#AppleMusic
                    🇧🇾#Belarus\1ului
                    #București
                    #BulevardulIuliuManiu
                    📈#BursaAmericană
                    #CancelarulGermaniei la 🏰#Cotroceni
                    🏔️#CarpațiiMeridionali & 🏔️#CarpațiiDeCurbură
                    #Cluj\1ean dezgustat de condițiile de la 🛒#Kaufland #Mănăștur!
                    centrala nucleară ☢️#Zaporijia
                    Comandantul-șef al Armatei Ucrainene declară că războiul cu 🇷🇺#Rusia se îndreaptă către etapa pozițională, a luptelor de uzură, care ar putea aduce beneficii rușilor. Cere aliaților noi capacități & tehnologii-cheie, cu accent pe puterea aeriană de foc.
                    #ComisiaJuridicăACamereiDeputaților
                    #CongresulAmerican
                    conturilor de la 📈#MinisterulFinanțelor
                    de la #ConsiliulEuropean
                    🌍#Europa caută să lupte împotriva valului de vehicule electrice chinezești, dar 🌍#europe\1nii le iubesc.
                    formațiune ☪️#islam\1ică
                    🇩🇪#GuvernulGermaniei confirmă
                    🌏#IndoPacific\1ă
                    în jurul parcării de la Opera ABCD
                    învățăturile ☪️#Coran\1ului sunt înțelepte
                    🇲🇦#Maroc. 👮#PolițiaMarocană declară
                    🇬🇧#RegatulUnit. 👮#PolițiaBritanică intensifică
                    🛡️#MinisterulApărării din 🇷🇺#Rusia
                    🛡️#MinistrulApărării din 🇮🇱#Israel
                    🌍#occident\1ali afurisiți
                    🌊#OceanulAtlantic, nu 🌊#OceanulIndian
                    🌊#OceanulAtlanticDeNord
                    🌍#Terra străbate un nor de praf lăsat de comenta ☄️#Halley
                    ⚖️#ParchetulEuropean
                    Pentru a ajunge pe 🌍#Terra.
                    📈#PiețeleEuropene avansează
                    🐦#Twitter e nașpa
                    Președinta pentru #ComisiaEuropeană (@EU_Commission@social.network.europa.eu) condamnă
                    Președinta pentru #ParlamentulEuropean: deputații din 🇺🇦#Ucraina & Republica 🇲🇩#Moldova ar putea să primească statutul de observatori
                    #PreședinteleBelarusului a cerut de la 🛡️#MinistrulApărării din 🇷🇺#Rusia
                    #PreședinteleEcuadorului a cerut
                    #PreședinteleSerbiei a dizolvat
                    #PreședinteleTaiwanului & cel pentru #CameraReprezentanților
                    prezentate de 🪖#armataIsraeliană
                    🏛️#PrimăriaCraiova caută artiști
                    Reportaj 📰#TheGuardian: Ambiția României pentru o nouă & vastă rezervație naturală, ca un ”🌋#Yellowstone al 🌍#Europe\1i”
                    Șeful pentru 🪖#ArmataRomână
                    🕵🏻‍♂️#ServiciileRuseDeInformații
                    🕵🏻‍♂️#ServiciileSpecialeItaliene
                    🕵🏻‍♂️#ServiciulUcraineanDeSecuritate
                    🕵🏻‍♂️#ServiciulRomânDeInformații
                    sistemele 🚀#HIMARS, rachete
                    🇺🇸#GuvernulStatelorUnite lansează
                    🇫🇷#SteagulFranței
                    Studiu. “Semnele vitale” ale Terrei sunt tot mai slabe
                    🇺🇸#SUA. #CongresulAmerican
                    #TârguMureș
                    #Tokmak-#Melitopol
                    Trafic blocat pe 🛣️#DN2, în aproprierea localității Traian
                    Urs semnalat în #RâmnicuVâlcea
                    📰#WashingtonPost: Unul dintre.""")

test_replacement("""Everything Everywhere all at Once
                    Game of Thrones
                    Harry Potter
                    Israel is one quarter the size of the state of Maine.
                    The city of Arad, located in western Romania, is home to the Arad Fortress, which was built in the late 18th century and is now a museum.
                    The religion of the majority of the population is Eastern Orthodox.""",
                 """🎞️#EverythingEverywhereAllAtOnce
                    🎞️#GameOfThrones
                    🎞️#HarryPotter
                    🇮🇱#Israel is one quarter the size of the state of #Maine.
                    The city of #Arad, located in western 🇷🇴#Romania, is home to the #AradFortress, which was built in the late #18Century and is now a museum.
                    The religion of the majority of the population is ☦️#Orthodox.""")
