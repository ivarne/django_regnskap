# -*- coding: utf-8 -*-
balanse = (
    (u'EIENDELER',(
        (u'Anleggsmiddler',(
            (u'Immaterielle eiendeler',(
                (u'Forskning og utvikling', '10'),
                (u'Konsesjoner, patenter, lisenser, varemerker og lignende rettigh.', '101'),
            )),
            (u'Varige driftsmidler',(
                (u'Tomter, bygninger og annen fast eiendom', '11'),
                (u'Andre anleggsmidler', '119'),
                (u'Driftsløsøre, inventar ol.', '12'),
            )),
            (u'Finansielle anleggsmiddler',(
                (u'Lån til foretak i samme konsern', '134'),
                (u'Investeringer i aksjer og andeler', '135'),
                (u'Obligasjoner og andre fordringer', '13'),
            )),
        )),
        (u'Omløpsmidler',(
            (u'Varer',(
                (u'Varer', '14'),
            )),
            (u'Fordringer',(
                (u'Kundefordringer', '150'),
                (u'Andre fordringer', ('15','16','17')),
            )),
            (u'Investeringer',(
                (u'Markedsbaserte aksjer', '181'),
                (u'Andre aksjer', '182'),
                (u'Markedsbaserte obligasjoner', '183'),
                (u'Andre obligasjoner', '18'),# egentlig 184, men vil helst fange ugyldige nummere også
            )),
            (u'Bankinnskudd, kontanter og lignende',(
                (u'Bankinnskudd, kontanter, og lignende', '19'),
            )),
        )),
    )),
    (u'EGENKAPITAL OG GJELD',(
        (u'Egenkapital',(
            (u'Innskutt egenkapital',(
                (u'Bundet egenkapital', ('200','101','202','203')),
            )),
            (u'Opptjent egenkapital',(
                (u'Fond for vurderingsforskjeller', '204'),
                (u'Annen egenkapital', '20'),
            )),
        )),
        (u'Gjeld',(
            (u'Avsetning for forpliktelser',(
                (u'Pensjonsforpliktelser', '210'),
                (u'Uopptjent inntekt', '216'),
                (u'Andre avsetninger for forpliktelser', '21'),# egentlig bare 218, men jeg vill fange alle nummer mellom også
            )),
            (u'Annen langsiktig gjeld',(
                (u'Konvertible lån', '220'),
                (u'Obligasjonslån', '221'),
                (u'Gjeld til kredittinstitusjoner', '222'),
                (u'Øvrig langsliktig gjeld', '22'),
            )),
            (u'Kortsiktig gjeld',(
                (u'Kortsiktige lån', '23'), # Hmm. hva er greia. her skal det være konvertible lån
#                (u'Sertifikatlån', None),
#                (u'Gjeld til kredittinstitusjoner', None),
                (u'Leverandørgjeld', '24'),
                (u'Betalbar skatt', '25'),
                (u'Skyldige offentlige avgifter', ('26','27')),
                (u'Utbytte', '28'),
                (u'Annen kortsiktig gjeld', '29'),
            )),
        )),
    )),
)

for overskrift, b in balanse:
    print overskrift #h2
    for hovedgrupe, h in b:
        print "\t", hovedgrupe #h3
        for undergruppe, u in h:
            print "\t\t", undergruppe #h4
            for kategori, key in u:
                print "\t\t\t", kategori , ': ' , key
                

resultat = (
    u'Inntekter',(
        (u'Salgsinntekter, avgiftspliktige', None),
        (u'Salgsinntekter, avgiftsfrie', None),
        (u'Salgsinntekter, utenfor avgiftsområdet', None),
        (u'Offentlige tilskudd', None),
        (u'Leieinntekter', None),
        (u'Andre inntekter', None),
    ),
    u'Kostnader',(
        (u'Varekostnad', None),
        (u'Lønn og annen godtgjørelse', None),
        (u'Annen driftskostnad', None),
    ),
    u'Finansposter og ekstraordinære poster',(
        (u'Finansinntekt', None),
        (u'Finanskostnad', None),
        (u'Ekstraordinær inntekt', None),
        (u'Ekstraordinær kostnad', None),
    ),
),