import re

def apply(text):
    text = text.replace('Anul Nou', '🎇#AnulNou')
    text = text.replace('Campionatul Mondial', '🏆#CampionatulMondial')
    text = re.sub('Cr[aă]ciun', '🎄#Craciun', text)
    text = re.sub('Cupa Mondial[aă]', '⚽#CupaMondială', text)
    text = text.replace('Electric Castle', '#ElectricCastle')
    text = text.replace('Gala Tinere Talente', '#GalaTinereTalente')
    text = text.replace('Gaudeamus 20', '#Gaudeamus20')
    text = re.sub('[Rr]oyal [Ee]vening', '#RoyalEvening', text)
    text = re.sub('Seara [Rr]egal[aă]', '#SearaRegală', text)
    text = text.replace('Seara Palatului Elisabeta', '#SearaPalatuluiElisabeta')

    # Awards
    text = re.sub('Ordinul Maica Domnului Rug[aă]toarea', '🏅#OrdinulMaicaDomnuluiRugătoarea', text)
    text = text.replace('Premiile Cantemir', '🏅#PremiileCantemir')

    # Music: Artists, Bands, etc
    text = text.replace('George Ezra', '#GeorgeEzra')
    text = text.replace('Iggy Pop', '#IggyPop')
    text = text.replace('The Chemical Brothers', '#TheChemicalBrothers')

    # Produse software
    text = text.replace('Android', '#Android')
    text = text.replace('Call of Duty', '#CallOfDuty')
    text = text.replace('Facebook', '#Facebook')
    text = text.replace('Fortnite', '#Fortnite')
    text = text.replace('iCloud', '#iCloud')
    text = text.replace('InSight', '#InSight')
    text = text.replace('Minecraft', '#Minecraft')
    text = text.replace('TikTok', '#TikTok')
    text = text.replace('Twitter', '#Twitter')
    text = text.replace('Windows', '#Windows')

    # Produse hardware
    text = text.replace('PC', '#PC')
    text = re.sub('Play[Ss]tation', '#PlayStation', text)
    text = re.sub('X[Bb]ox', '#XBox', text)

    text = text.replace('Artemis I', '🚀#ArtemisI')
    text = text.replace('Autostrada A', '🛣️#AutostradaA')
    text = text.replace('Capsula Orion', '🛰️#CapsulaOrion')
    text = text.replace('Eurofighter', '🛩️#Eurofighter')
    text = re.sub('F[-]*16', '🛩️#F16', text)
    text = re.sub('F[-]*35B', '🛩️#F35B', text)
    text = text.replace('Grupa F', '#GrupaF')
    text = text.replace('HIMARS', '🚀#HIMARS')
    text = re.sub('Java', '#Java', text)
    text = re.sub('JDAM', '#JDAM', text)
    text = re.sub('Mi[Gg]-', '🛩️#MiG', text)
    text = text.replace('Ora Regelui', '👑#OraRegelui')
    text = re.sub('P[aă]m[aâ]nt ', '🌍#Pământ ', text)
    text = re.sub('P[aă]m[aâ]nt\.', '🌍#Pământ\.', text)
    text = re.sub('P[aă]m[aâ]nt,', '🌍#Pământ,', text)
    text = text.replace('PNRR', '#PNRR')
    text = text.replace('Rabla pentru Electrocasnice', '♻️#RablaPentruElectrocasnice')
    text = text.replace('RMN', '#RMN')
    text = text.replace('Sarmat', '🚀#Sarmat')
    text = re.sub('Scheng[h]*en', '🛂#Schengen', text)
    text = text.replace('Shahed', '🛩️#Shahed')
    text = text.replace('Tomahawk', '🚀#Tomahawk')
    text = text.replace('Vega-C', '🚀#VegaC')
    text = text.replace('Watchkeeper X', '🛩️#WatchkeeperX')

    text = text.replace('ADN', '🧬#ADN')
    text = re.sub('[Aa]lerta [Dd]e [Vv]iscol', '🌨️#AlertaDeViscol', text)
    text = re.sub('[Aa]lertă [Dd]e [Vv]iscol', '🌨️#AlertăDeViscol', text)
    text = text.replace('Alzheimer', '#Alzheimer')
    text = re.sub('[Aa]saltul [Aa]supra [Cc]apitoliului', '#AsaltulAsupraCapitoliului', text)
    text = text.replace('Brent', '🛢️#Brent')
    text = re.sub('[Cc]od [Gg]alben', '🟡#CodGalben', text)
    text = re.sub('[Cc]od [Pp]ortocaliu', '🟠#CodPortocaliu', text)
    text = re.sub('[Cc]od [Rr]o[sș]u', '🔴#CodRoșu', text)
    text = re.sub('C[Oo][Vv][Ii][Dd]', '🦠#COVID', text)
    text = text.replace('cryptomonede', '🪙#cryptomonede')
    text = re.sub('[Ee]poca [Mm]igra[tț]iilor', '🪓#EpocaMigrațiilor', text)
    text = text.replace('EULEX', '#EULEX')
    text = text.replace('fentanil', '#fentanil')
    text = text.replace('fotovoltaice', '#fotovoltaice')
    text = text.replace('heroina', '#heroina')
    text = text.replace('heroină', '#heroină')
    text = re.sub('[Ii]nsurec[tț]ia [Dd]e [Ll]a [Cc]apitoliu', '#AsaltulAsupraCapitoliului', text)
    text = text.replace('INVESTIGAȚIE RECORDER', '🔴#InvestigațieRecorder')
    text = text.replace('Mistral', '🚀#Mistral')
    text = text.replace('Patriot', '🚀#Patriot')
    text = re.sub('Petrolul [Ee]uropean', '🛢️#PetrolulEuropean', text)
    text = re.sub('Planul [Rr]o[sș]u', '🟥#PlanulRoșu', text)
    text = re.sub('[Rr][aă]scoala [Dd]e [Ll]a [Cc]apitoliu', '#AsaltulAsupraCapitoliului', text)
    text = re.sub('[Rr][aă]zboiul [Rr]ece', '#RăzboiulRece', text)
    text = re.sub('Stare [Dd]e [Uu]rgen[tț][aă]', '🚨#StareDeUrgență', text)
    text = re.sub('[Ss]tiff[ -][Pp]erson', '#StiffPerson', text)
    text = re.sub('[Tt]ranzi[tț]ia [Vv]erde', '🍃#TranzițiaVerde', text)
    text = text.replace('zero emisii( de carbon)*', '🍃#ZeroEmisii')

    # Companies
    text = text.replace('Activision', '#Activision')
    text = text.replace('Amazon', '#Amazon')
    text = text.replace('Airbus', '#Airbus')
    text = text.replace('Apple', '#Apple')
    text = text.replace('Azovstal', '#Azovstal')
    text = text.replace('Blizzard', '#Blizzard')
    text = text.replace('CFR', '#CFR')
    text = text.replace('Dacia', '🚗#Dacia')
    text = text.replace('Enel', '#Enel')
    text = text.replace('EpicGames', '🎮#EpicGames')
    text = text.replace('Erste', '#Erste')
    text = text.replace('Google', '#Google')
    text = text.replace('KARSAN', '#KARSAN')
    text = text.replace('Mediawan', '#Mediawan')
    text = text.replace('Mercedes Benz', '🚗#MercedesBenz')
    text = text.replace('Mercedes', '🚗#Mercedes')
    text = text.replace('Meta', '#Meta')
    text = text.replace('Microsoft', '#Microsoft')
    text = text.replace('Nikola', '#Nikola')
    text = text.replace('Neuralink', '#Neuralink')
    text = text.replace('Pan Am', '✈️#PanAm')
    text = text.replace('Porsche', '🚗#Porsche')
    text = text.replace('Roscosmos', '🚀#Roscosmos')
    text = text.replace('Rosneft', '#Rosneft')
    text = text.replace('Sony', '#Sony')
    text = text.replace('SpaceX', '🚀#SpaceX')
    text = text.replace('Tesla', '#Tesla')

    # Companies - Financial
    text = text.replace('Banca Angliei', '🏦#BancaAngliei')
    text = re.sub('[Bb][aă]nc(a|ii) [Cc]entral[aăe] [Ee]urope[a]*n[aăe]', '🏦#BCE', text)
    text = text.replace('BCE', '🏦#BCE')
    text = text.replace('BCR', '🏦#BCR')
    text = text.replace('BNR', '🏦#BNR')
    text = text.replace('FTX', '📈#FTX')
    text = text.replace('ING', '🏦#ING')

    # Companies - News
    text = text.replace('BBC', '📰#BBC')
    text = text.replace('Biziday', '📰#Biziday')
    text = text.replace('CNBC', '📰#CNBC')
    text = text.replace('CNN', '📰#CNN')
    text = text.replace('FT', '📰#FinancialTimes')
    text = text.replace('Financial Times', '📰#FinancialTimes')
    text = text.replace('Fox News', '📰#FoxNews')
    text = text.replace('NY Times', '📰#NYTimes')
    text = text.replace('Politico', '📰#Politico')
    text = re.sub('Presa [Aa]merican[aă]', '📰#PresaAmericană', text)
    text = re.sub('Presa [Ii]nterna[tț]ional[aă]', '📰#PresaInternațională', text)
    text = re.sub('Presa [Rr]us[aă]', '📰#PresaRusă', text)
    text = text.replace('Reuters', '📰#Reuters')
    text = text.replace('Sky News', '📰#SkyNews')
    text = text.replace('The Guardian', '📰#TheGuardian')
    text = re.sub('(The )*Washington Post', '📰#WashingtonPost', text)

    # Companii, organizații
    text = re.sub('Agen[tț]ia [Ss]pa[tț]ial[aă] [Ee]uropean[aă]', '🚀#AgențiaSpațialăEuropeană', text)
    text = text.replace('Ambasada Ucrainei', '#AmbasadaUcrainei')
    text = text.replace('ANAF', '#ANAF')
    text = text.replace('ANCOM', '#ANCOM')
    text = re.sub('Arhivele [Nn]a[tț]ionale', '🗄️#ArhiveleNaționale', text)
    text = re.sub('[Aa]rmata [Rr]om[aâ]n([aă]|iei)', '🪖#ArmataRomână', text)
    text = re.sub('[Aa]rmata [Rr]us[aă]', '🪖#ArmataRusă', text)
    text = re.sub('[Aa]rmata [Uu]crainean[aă]', '🪖#ArmataUcraineană', text)
    text = re.sub('[Aa]utorit[aă][tț]ile [Ff]ranceze', '👮#AutoritățileFranceze', text)
    text = text.replace('BND', '#BND')
    text = re.sub('[Cc]amera [Dd]eputa[tț]ilor', '#CameraDeputaților', text)
    text = re.sub('[Cc]amera [Rr]eprezentan[tț]ilor', '#CameraReprezentanților', text)
    text = re.sub('[Cc]asa [Aa]lb[aă]', '#CasaAlbă', text)
    text = text.replace('CFA', '#CFA')
    text = text.replace('CJUE', '⚖️#CurteaDeJustițieUE')
    text = re.sub('[Cc]omisia [Ee]uropean[aă]', '#ComisiaEuropeană (@EU_Commission@social.network.europa.eu)', text)
    text = text.replace('Congres ', '#Congres ')
    text = text.replace('Congres.', '#Congres.')
    text = text.replace('Congres,', '#Congres,')
    text = re.sub('[Cc]ongresul [Aa]merican', '#CongresulAmerican', text)
    text = re.sub('[Cc]onsiliul [Cc]oncuren[tț]ei', '#ConsiliulConcurenței', text)
    text = re.sub('[Cc]onsiliul [Ee]uropean', '#ConsiliulEuropean', text)
    text = re.sub('[Cc]onsiliul [Gg]eneral', '#ConsiliulGeneral', text)
    text = re.sub('[Cc]onsiliul [Nn]a[tț]ional [Aa]l [Ee]levilor', '#ConsiliulNaționalAlElevilor', text)
    text = re.sub('[Cc]orpul [Dd]iplomatic', '📜#CorpulDiplomatic', text)
    text = re.sub('Crucea Ro[sș]ie', '🏥#CruceaRoșie', text)
    text = text.replace('Curtea de Conturi', '#CurteaDeConturi')
    text = text.replace('Curtea de Justiție( a)* UE', '⚖️#CurteaDeJustițieUE')
    text = re.sub('[Dd]iplomatic [Cc]orps', '📜#DiplomaticCorps', text)
    text = text.replace('DNA', '#DNA')
    text = text.replace('DVSA', '#DVSA')
    text = text.replace('FBI', '👮#FBI')
    text = re.sub('[Ff]or[tț]ele [Aa]eriene', '✈️#ForțeleAeriene', text)
    text = re.sub('[Ff]or[tț]ele [Nn]avale [Rr]om[aâ]ne', '⚓#ForțeleNavaleRomâne', text)
    text = text.replace('Înalta Curte', '#ÎnaltaCurte')
    text = text.replace('ISW', '#ISW')
    text = text.replace('JAI', '#JAI')
    text = text.replace('NASA', '🚀#NASA')
    text = text.replace('Ordinul de Malta', '🗡️#OrdinulDeMalta')
    text = text.replace('OMS', '🏥#OMS')
    text = re.sub('[Pp]arlament\.', '#Parlament.', text)
    text = text.replace('Parlamentul European', '#ParlamentulEuropean')
    text = re.sub('Pentagonul', '#Pentagon-ul', text)
    text = re.sub('Pentagon', '#Pentagon', text)
    text = text.replace('Plug Power', '#PlugPower')
    text = re.sub('Poli[tț]ia [Dd]e [Ff]rontier[aă]', '👮#PolițiaDeFrontieră', text)
    text = re.sub('Por[tț]ile [Dd]e [Ff]ier[ ]*', '#PorțileDeFier', text)
    text = re.sub('Salva[tț]i [Cc]opiii', '#SalvațiCopiii', text)
    text = re.sub('Serviciul de Informa[tț]ii [Ee]xterne', '#ServiciulDeInformațiiExterne', text)
    text = re.sub('Serviciul de Informa[tț]ii [sș]i Securitate', '#ServiciulDeInformațiiȘiSecuritate', text)

    # Partide RO
    text = text.replace('AUR', '#AUR')
    text = text.replace('PNL', '#PNL')
    text = text.replace('PPE', '#PPE')
    text = text.replace('PSD', '#PSD')
    text = text.replace('UDMR', '#UDMR')
    text = text.replace('USR', '#USR')

    # Oficiali RO
    text = text.replace('Ambasadorul Germaniei', '#AmbasadorulGermaniei')
    text = re.sub('[Cc]ustodele [Cc]oroanei', '👑CustodeleCoroanei', text)
    text = text.replace('MAE', '📜#MAE')
    text = re.sub('Minist[e]*rul (Afacerilor|de) Externe', '📜#MAE', text)
    text = text.replace('Ministrul Agriculturii', '🚜#MinistrulAgriculturii')
    text = re.sub('Ministrul Ap[aă]r[aă]rii', '🛡️#MinistrulApărării', text)
    text = re.sub('Ministru[l]*( al)* [Ee]conomiei', '#MinistrulEconomiei', text)
    text = re.sub('Ministrul ucrainean al Ap[aă]r[aă]rii', '#MinistrulApărării din Ucraina', text)
    text = text.replace('Ministrul de Interne', '#MinistrulDeInterne')
    text = re.sub('Ministrul Educa[tț]iei', '🎓#MinistrulEducației', text)
    text = text.replace('Ministrul Energiei', '⚡#MinistrulEnergiei')
    text = text.replace('Ministrul Mediului', '🏞️#MinistrulMediului')
    text = re.sub('Ministerul Ap[aă]r[aă]rii', '🛡️#MinisterulApărării', text)
    text = text.replace('Ministerul S[aă]n[aă]t[aă][tț]ii', '🏥#MinisterulSănătății')
    text = re.sub('Ministerul [Tt]ransporturilor', '🛤️#MinisterulTransporturilor', text)
    text = re.sub('[Pp]remierul', 'Prim-Ministrul', text)
    text = re.sub('[Pp]re[sș]edintele Elve[tț]iei', '#PreședinteleElveției', text)
    text = re.sub('[Pp]re[sș]edintele Ucrainei', '#PreședinteleUcrainei', text)
    text = re.sub('[Pp]rim[ -][Mm]inistrul [Bb]ritanic', '#PrimMinistrulMariiBritanii', text)
    text = re.sub('[Pp]rim[ -][Mm]inistrul [Kk]osovar', '#PrimMinistrulKosovoului', text)
    text = re.sub('[Pp]rim[ -][Mm]inistrul Serbiei', '#PrimMinistrulSerbiei', text)
    text = re.sub('[Pp]rim[ -][Mm]inistrul', '#PrimMinistrul', text)

    # Oficiali străini
    text = text.replace('Cancelarul Austriei', '#CancelarulAustriei')
    text = re.sub('Vicepre[sș]edintele Parlamentului European', '🇪🇺#VicepreședinteleParlamentuluiEuropean', text)

    # Persoane RO
    text = re.sub('B[aă]d[aă]l[aă]u', '#Bădălău', text)
    text = re.sub('Bogdan Vod[aă]', '#BogdanVodă', text)
    text = text.replace('Chesnoiu', '#Chesnoiu')
    text = re.sub('Ciuc[aă]', '#Ciucă', text)
    text = re.sub('Cristi D[aă]nile[tț]', '#CristiDănileț', text)
    text = text.replace('David Popovici', '#DavidPopovici')
    text = text.replace('Grindeanu', '#Grindeanu')
    text = text.replace('Iohannis', '#Iohannis')
    text = text.replace('Kovesi', '#Kovesi')
    text = text.replace('Lucian Bode', '#LucianBode')
    text = text.replace('Mihai Țurcanu', '#MihaiȚurcanu')
    text = text.replace('Roman ', '#Roman ')
    text = text.replace('Roman.', '#Roman.')
    text = text.replace('Roman,', '#Roman,')

    # Persons - foreign
    text = text.replace('Ben Hodges', '#BenHodges')
    text = text.replace('Benzema', '#Benzema')
    text = text.replace('Biden', '#Biden')
    text = text.replace('Blinken', '#Blinken')
    text = text.replace('Boris Becker', '#BorisBecker')
    text = text.replace('Brad Pitt', '#BradPitt')
    text = text.replace('Brittney Griner', '#BrittneyGriner')
    text = text.replace('Castillo', '#Castillo')
    text = text.replace('Celine Dion', '#CelineDion')
    text = re.sub('Charles( al)* III(\-lea)*', '#CharlesIII', text)
    text = text.replace('Elon Musk', '#ElonMusk')
    text = text.replace('Erdogan', '#Erdogan')
    text = text.replace('Eva Kaili', '#EvaKaili')
    text = text.replace('Giroud', '#Giroud')
    text = text.replace('Kaili', '#Kaili')
    text = text.replace('Kavalec', '#Kavalec')
    text = text.replace('Kennedy', '#Kennedy')
    text = text.replace('Macron', '#Macron')
    text = text.replace('Manfred Weber', '#ManfredWeber')
    text = text.replace('Medvedev', '#Medvedev')
    text = text.replace('Messi', '#Messi')
    text = text.replace('Musk', '#Musk')
    text = text.replace('Nehammer', '#Nehammer')
    text = text.replace('Charles de Gaulle', '#CharlesDeGaulle')
    text = text.replace('James Cameron', '#JamesCameron')
    text = re.sub('Petru [Cc]el Mare', '#PetruCelMare', text)
    text = text.replace('Putin', '#Putin')
    text = text.replace('Rogozin', '#Rogozin')
    text = text.replace('Scholz', '#Scholz')
    text = text.replace('Șoigu', '#Șoigu')
    text = text.replace('Stoltenberg', '#Stoltenberg')
    text = text.replace('Trump', '#Trump')
    text = re.sub('Viktor Orb[aá]n', '#ViktorOrban', text)
    text = re.sub('Viktor Bout', '#ViktorBout', text)
    text = text.replace('Wagner', '#Wagner')
    text = re.sub('Zelensk[iy][iy]*', '#Zelensky', text)

    # Filme
    text = re.sub('Avatar( 2)*(: | [–-] )The Way of Water', '#AvatarTheWayOfWater', text)
    text = text.replace('Monty Python', '#MontyPython')

    # Zone geografice
    text = re.sub('America [Cc]entral[aă]', '🌎#AmericaCentrală', text)
    text = re.sub('America [Dd]e [Nn]ord', '🌎#AmericaDeNord', text)
    text = re.sub('America [Dd]e [Ss]ud', '🌎#AmericaDeSud', text)
    text = text.replace('Ardeal', '#Ardeal')
    text = text.replace('Balcanii de Vest', '#BalcaniiDeVest')
    text = text.replace('Banat', '#Banat')
    text = text.replace('Basarabia', '#Basarabia')
    text = text.replace('Bucovina', '#Bucovina')
    text = re.sub('Carpații ', '🏔️#Carpații', text)
    text = re.sub('Carpați', '🏔️#Carpați', text)
    text = text.replace('Dobrogea', '#Dobrogea')
    text = re.sub('Dun[aă]re', '#Dunăre', text)
    text = re.sub('[Ee]stul Europei', '🌍#EuropaDeEst', text)
    text = re.sub('Europa [Dd]e [Ee]st', '🌍#EuropaDeEst', text)
    text = text.replace('Europa', '🌍#Europa')
    text = text.replace('Extremul Orient Rus', '#ExtremulOrientRus')
    text = text.replace('Indo-Pacific', '🌏#IndoPacific')
    text = re.sub('Marea Baltic[aă]', '🌊#MareaBaltică', text)
    text = re.sub('Marea Neagr[aă]', '🌊#MareaNeagră', text)
    text = text.replace('Muntenia', '#Muntenia')
    text = re.sub('Mun[tț]ii [#]*Banatului', '🏔️#MunțiiBanatului', text)
    text = text.replace('Occident.', '#Occident.')
    text = text.replace('Occident,', '#Occident,')
    text = text.replace('Occident ', '#Occident ')
    text = text.replace('Oceanul ', '#Oceanul')
    text = text.replace('Oltenia', '#Oltenia')
    text = text.replace('Transilvania', '#Transilvania')
    text = text.replace('Valea Oltului', '#ValeaOltului')
    text = text.replace('Vulcanul Fuego', '🌋#VulcanulFuego')
    text = re.sub('Zona Seismic[aă]', '#ZonaSeismică', text)
    
    # Localități RO
    text = text.replace('Agigea', '#Agigea')
    text = re.sub('Alba[ -]Iulia', '#AlbaIulia', text)
    text = text.replace('Arad', '#Arad')
    text = re.sub('Bac[aă]u', '#Bacău', text)
    text = re.sub('Baia [Dd]e Aram[aă]', '#BaiaDeAramă', text)
    text = re.sub('Baia[ -]Mare', '#BaiaMare', text)
    text = re.sub('B[aă]ile Herculane', '#BăileHerculane', text)
    text = re.sub('Boi[tț]a', '#Boița', text)
    text = re.sub('Boto[sș]ani', '#Botosani', text)
    text = re.sub('Br[aă]ila', '#Brăila', text)
    text = re.sub('Bra[sș]ov', '#Brasov', text)
    text = re.sub('Bucure[sș]ti', '#București', text)
    text = text.replace('Buteni', '#Buteni')
    text = re.sub('Buz[aă]u', '#Buzău', text)
    text = re.sub('Caransebe[sș]', '#Caransebeș', text)
    text = re.sub('C[aâ]mpia Turzii', '#CampiaTurzii', text)
    text = re.sub('Chi[sș]inău', '#Chisinău', text)
    text = text.replace('Ciucea', '#Ciucea')
    text = re.sub('Cluj[ -]Napoca', '#ClujNapoca', text)
    text = re.sub('Constan[tț]a', '#Constanța', text)
    text = text.replace('Copaciu', '#Copaciu')
    text = text.replace('Craiova', '#Craiova')
    text = re.sub('Drobeta[ -]Turnu[ -]Severin', '#DrobetaTurnuSeverin', text)
    text = re.sub('Gala[tț]i', '#Galati', text)
    text = text.replace('Giurgiu', '#Giurgiu')
    text = text.replace('Huedin', '#Huedin')
    text = re.sub('Ia[sș]i', '#Iasi', text)
    text = text.replace('Lugoj', '#Lugoj')
    text = re.sub('Moine[sș]ti', '#Moinești', text)
    text = re.sub('N[aă]d[aă][sș]elu', '#Nădășelu', text)
    text = re.sub('N[aă]dlac', '#Nădlac', text)
    text = re.sub('Neam[tț]', '#Neamt', text)
    text = text.replace('Negreni', '#Negreni')
    text = re.sub('Ob[aâ]r[sș]ia Clo[sș]ani', '#ObrășiaCloșani', text)
    text = text.replace('Oradea', '#Oradea')
    text = re.sub('Or[sș]ova', '#Orsova', text)
    text = text.replace('Ovidiu', '#Ovidiu')
    text = re.sub('Pite[sș]ti', '#Pitești', text)
    text = re.sub('Ploie[sș]ti', '#Ploiești', text)
    text = re.sub('R[aă]zboieni', '#Razboieni', text)
    text = re.sub('S[aă]li[sș]te', '#Săliște', text)
    text = re.sub('S[aă]v[aâ]r[sș]in', '#Săvârșin', text)
    text = text.replace('Satu Mare', '#SatuMare')
    text = re.sub('Sebe[sș]', '#Sebeș', text)
    text = text.replace('Slatina', '#Slatina')
    text = text.replace('Suceava', '#Suceava')
    text = re.sub('T[aâ]rgu Frumos', '#TârguFrumos', text)
    text = re.sub('T[aâ]rgu Jiu', '#TârguJiu', text)
    text = re.sub('T[aâ]rguMure[sș]', '#TârguMureș', text)
    text = text.replace('Tecuci', '#Tecuci')
    text = re.sub('Teiu[sș]i', '#Teiuși', text)
    text = re.sub('Timi[sș]oara', '#Timisoara', text)
    text = re.sub('Ti[sș]i[tț]a', '#Tișița', text)
    text = text.replace('Sibiu', '#Sibiu')
    text = re.sub('Sine[sș]ti', '#Sinești', text)
    text = text.replace('Urziceni', '#Urziceni')
    text = re.sub('Vaslui', '#Vaslui', text)
    text = re.sub('Z[aă]gujeni', '#Zăgujeni', text)
    text = re.sub('Zal[aă]u', '#Zalau', text)

    # Localități străine
    text = text.replace('Ankara', '#Ankara')
    text = text.replace('Barcelona', '#Barcelona')
    text = text.replace('Bakhmut', '#Bakhmut')
    text = text.replace('Beijing', '#Beijing')
    text = text.replace('Belgorod', '#Belgorod')
    text = text.replace('Belgrad', '#Belgrad')
    text = text.replace('Berlin', '#Berlin')
    text = text.replace('Brno', '#Brno')
    text = text.replace('Birmingham', '#Birmingham')
    text = text.replace('Bruxelles', '#Bruxelles')
    text = text.replace('Budapest', '#Budapest')
    text = re.sub('C[h]*ernihiv', '#Chernihiv', text)
    text = text.replace('Dresda', '#Dresda')
    text = text.replace('Dresden', '#Dresden')
    text = text.replace('Harkov', '#Harkov')
    text = text.replace('Istanbul', '#Istanbul')
    text = re.sub('Ki[ey]v', '#Kiev', text)
    text = text.replace('Kramatorsk', '#Kramatorsk')
    text = text.replace('Lockerbie', '#Lockerbie')
    text = text.replace('Londra', '#Londra')
    text = text.replace('Lyon', '#Lyon')
    text = text.replace('Madrid', '#Madrid')
    text = text.replace('Mariupol', '#Mariupol')
    text = text.replace('Melbourne', '#Melbourne')
    text = text.replace('Melitopol', '#Melitopol')
    text = text.replace('Minsk', '#Minsk')
    text = text.replace('Montpellier', '#Montpellier')
    text = text.replace('Moscova', '#Moscova')
    text = text.replace('New York', '#NewYork')
    text = re.sub('Odes[s]*a', '#Odesa', text)
    text = text.replace('Paris', '#Paris')
    text = text.replace('Pristina', '#Pristina')
    text = text.replace('Priștina', '#Priștina')
    text = text.replace('Riad', '#Riad')
    text = re.sub('R[ey]azan', '#Ryazan', text)
    text = text.replace('Shanghai', '#Shanghai')
    text = text.replace('Sloviansk', '#Sloviansk')
    text = text.replace('Sofia', '#Sofia')
    text = re.sub('Sum[iîy]', '#Sumy', text)
    text = text.replace('Teheran', '#Teheran')
    text = text.replace('Viena', '#Viena')
    text = text.replace('Washingtonul', 'Washington-ul')
    text = text.replace('Washington', '#Washington')
    text = text.replace('Zagreb', '#Zagreb')

    # Buildings, Streets, Neighbourhoods - RO
    text = re.sub('Castelul [Rr]egal', '🏰#CastelulRegal', text)
    text = re.sub('Centura [Dd]e [Vv]est', '#CenturaDeVest', text)
    text = re.sub('Moara [Dd]e V[aâ]nt', '#MoaraDeVânt', text)
    text = text.replace('Otopeni', '✈️#Otopeni')
    text = text.replace('Palatul Elisabeta', '🏰#PalatulElisabeta')
    text = text.replace('Palatul Victoria', '🏰#PalatulVictoria')

    # Buildings, Streets, Neighbourhoods - foreign
    text = text.replace('Brandenburg', '#Brandenburg')
    text = text.replace('Charles de Gaulle', '✈️#CharlesDeGaulle')
    text = text.replace('IIS', '🛰️#IIS')
    text = text.replace('Nord Stream', '⛽#NordStream')
    text = text.replace('Orly', '✈️#Orly')
    text = text.replace('Radisson Blu', '🏨#RadissonBlu')
    text = re.sub('Sta[tț]ia [Ss]pa[tț]ial[aă] Interna[tț]ional[aă]', '🛰️#StațiaSpațialăInternațională', text)
    text = re.sub('Trapani[ -]Birgi', '✈️#TrapaniBirgi', text)

    # Regiuni RO
    text = text.replace('Bihor', '#Bihor')
    text = re.sub('Cara[sș][ -]Severin', '#CarașSeverin', text)
    text = text.replace('Cluj', '#Cluj')
    text = text.replace('Covasna', '#Covasna')
    text = text.replace('Dolj', '#Dolj')
    text = text.replace('Gorj', '#Gorj')
    text = text.replace('Harghita', '#Harghita')
    text = re.sub('Ialomi[tț]a', '#Ialomița', text)
    text = text.replace('Ilfov', '#Ilfov')
    text = re.sub('Mehedin[tț]i', '#Mehedinti', text)
    text = re.sub('Mure[sș]', '#Mureș', text)
    text = re.sub('S[aă]laj', '#Sălaj', text)
    text = text.replace('Teleorman', '#Teleorman')
    text = re.sub('Timi[sș]', '#Timiș', text)
    text = text.replace('Tulcea', '#Tulcea')
    text = text.replace('Vrancea', '#Vrancea')

    # Regiuni străine
    text = text.replace('Baja California', '#BajaCalifornia')
    text = text.replace('California', '#California')
    text = text.replace('Crimeea', '#Crimeea')
    text = re.sub('Done[tț]k', '#Donetsk', text)
    text = text.replace('Florida', '#Florida')
    text = text.replace('Golful Persic', '#GolfulPersic')
    text = text.replace('Luhansk', '#Luhansk')
    text = text.replace('Sicilia', '#Sicilia')
    text = text.replace('Texas', '#Texas')
    text = text.replace('Zaporijie', '#Zaporozhye')

    text = re.sub('Jupiter', '🪐#Jupiter', text)
    text = re.sub('Lun[aă]', '🌙#Luna', text)
    text = re.sub('Marte', '🪐#Marte', text)

    # Țări
    text = text.replace('Afganistan', '🇦🇫#Afganistan')
    text = text.replace('Afghanistan', '🇦🇫#Afghanistan')
    text = text.replace('Anglia', '🏴󠁧󠁢󠁥󠁮󠁧󠁿#Anglia')
    text = text.replace('Argentina', '🇦🇷#Argentina')
    text = text.replace('Australia', '🇦🇺#Australia')
    text = text.replace('Austria', '🇦🇹#Austria')
    text = text.replace('Belarus', '🇧🇾#Belarus')
    text = text.replace('Belgia', '🇧🇪#Belgia')
    text = text.replace('Bosnia', '🇧🇦#Bosnia')
    text = text.replace('Brazilia', '🇧🇷#Brazilia')
    text = text.replace('Bulgaria', '🇧🇬#Bulgaria')
    text = text.replace('Camerun', '🇨🇲#Camerun')
    text = text.replace('Canada', '🇨🇦#Canada')
    text = text.replace('Cehia', '🇨🇿#Cehia')
    text = text.replace('China', '🇨🇳#China')
    text = text.replace('Chile', '🇨🇱#Chile')
    text = text.replace('Coreea de Nord', '🇰🇵#CoreeaDeNord')
    text = text.replace('Coreea de Sud', '🇰🇷#CoreeaDeSud')
    text = text.replace('Costa Rica', '🇨🇷#CostaRica')
    text = re.sub('Croa[tț]ia', '🇭🇷#Croatia', text)
    text = text.replace('Danemarca', '🇩🇰#Danemarca')
    text = re.sub('Elve[tț]ia', '🇨🇭#Elveția', text)
    text = text.replace('Estonia', '🇪🇪#Estonia')
    text = text.replace('Finlanda', '🇫🇮#Finlanda')
    text = re.sub('Fran[tț]a', '🇫🇷#Franța', text)
    text = text.replace('Georgia', '🇬🇪#Georgia')
    text = text.replace('Germania', '🇩🇪#Germania')
    text = text.replace('Ghana', '🇬🇭#Ghana')
    text = text.replace('Grecia', '🇬🇷#Grecia')
    text = text.replace('Guatemala', '🇬🇹#Guatemala')
    text = text.replace('Hong Kong', '🇭🇰#HongKong')
    text = text.replace('India', '🇮🇳#India')
    text = text.replace('Indonezia', '🇮🇩#Indonezia')
    text = text.replace('Iran ', '🇮🇷#Iran ')
    text = text.replace('Iran.', '🇮🇷#Iran.')
    text = text.replace('Iran,', '🇮🇷#Iran,')
    text = text.replace('Islanda', '🇮🇸#Islanda')
    text = text.replace('Israel', '🇮🇱#Israel')
    text = text.replace('Italia', '🇮🇹#Italia')
    text = text.replace('Japonia', '🇯🇵#Japonia')
    text = text.replace('Kosovo', '🇽🇰#Kosovo')
    text = text.replace('Letonia', '🇱🇻#Letonia')
    text = text.replace('Lituania', '🇱🇹#Lituania')
    text = text.replace('Marea Britanie', '🇬🇧#MareaBritanie')
    text = text.replace('Malta', '🇲🇹#Malta')
    text = text.replace('Maroc ', '🇲🇦#Maroc ')
    text = text.replace('Maroc,', '🇲🇦#Maroc,')
    text = text.replace('Maroc.', '🇲🇦#Maroc.')
    text = text.replace('Moldova', '🇲🇩#Moldova')
    text = text.replace('Norvegia', '🇳🇴#Norvegia')
    text = text.replace('Olanda', '🇳🇱#Olanda')
    text = text.replace('Peru', '🇵🇪#Peru')
    text = text.replace('Polonia', '🇵🇱#Polonia')
    text = text.replace('Portugalia', '🇵🇹#Portugalia')
    text = text.replace('Qatar', '🇶🇦#Qatar')
    text = re.sub('Rom[aâ]nia', '🇷🇴#Romania', text)
    text = text.replace('Rusia', '🇷🇺#Rusia')
    text = re.sub('Sco[tț]ia', '🏴󠁧󠁢󠁳󠁣󠁴󠁿#Scotia', text)
    text = text.replace('Senegal', '🇸🇳#Senegal')
    text = text.replace('Serbia', '🇷🇸#Serbia')
    text = text.replace('Siria', '🇸🇾#Siria')
    text = text.replace('Slovacia', '🇸🇰#Slovacia')
    text = text.replace('Slovenia', '🇸🇮#Slovenia')
    text = text.replace('Spania', '🇪🇸#Spania')
    text = re.sub('Statel[eo][r]* Unite( ale Americii)*', '🇺🇸#SUA', text)
    text = text.replace('SUA', '🇺🇸#SUA')
    text = text.replace('Suedia', '🇸🇪#Suedia')
    text = text.replace('Taiwan', '🇹🇼#Taiwan')
    text = text.replace('Turcia', '🇹🇷#Turcia')
    text = text.replace('Ucraina', '🇺🇦#Ucraina')
    text = text.replace('Ungaria', '🇭🇺#Ungaria')
    text = text.replace('Uruguay', '🇺🇾#Uruguay')
    text = text.replace('Venezuela', '🇻🇪#Venezuela')

    text = text.replace('Stat Islamic', '#StatIslamic')

    # Country groups
    text = text.replace('G7', '#G7')
    text = text.replace('NATO', '#NATO')
    text = text.replace('ONU', '🇺🇳#ONU')
    text = text.replace('Statele Europene', '#StateleEuropene')
    text = text.replace('Țările Baltice', '#ȚărileBaltice')
    text = text.replace(' UE', ' 🇪🇺#UE')
    text = re.sub('^UE', '🇪🇺#UE', text)
    text = re.sub('Uniun[ei][ai] Europe[a]*n[aăe]', '🇪🇺#UE', text)

    text = text.replace('#Elon#Musk', '#ElonMusk')
    text = text.replace('🏔️#🏔️#', '🏔️#')
    text = text.replace('🌍#🌍#', '🌍#')
    text = re.sub('#[#]*', '#', text)

    return text
