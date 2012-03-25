# -*- coding: utf-8 -*-

from models import Konto

kontos = [
{"nummer": 3920 ,"navn": u"Medlemskontigent"},
{"nummer": 3403 ,"navn": u"Stud. sos. midler"},
{"nummer": 3402 ,"navn": u"Kommunal støtte"},
{"nummer": 3401 ,"navn": u"Repromidler"},
{"nummer": 3400 ,"navn": u"Frifondsmidler"},
{"nummer": 3441 ,"navn": u"Andre tilskudd"},
{"nummer": 3911 ,"navn": u"Inntekter arr"},
{"nummer": 3200 ,"navn": u"Salg Kjøkkengruppa"},
{"nummer": 3201 ,"navn": u"Salg Åpenbaringen"},
{"nummer": 3202 ,"navn": u"Inntekter T&W"},
{"nummer": 3203 ,"navn": u"Salg av T-skjorter"},
{"nummer": 3910 ,"navn": u"Inntekter  Alpha"},
{"nummer": 3970 ,"navn": u"Kollekt inn"},
{"nummer": 3971 ,"navn": u"Diverse gaver"},
{"nummer": 3972 ,"navn": u"Fast givere"},
{"nummer": 8040 ,"navn": u"Renteinntekter"},
{"nummer": 8400 ,"navn": u"Ekstra ordinær inntekt"},
#Kostnader
{"nummer": 6300 ,"navn": u"Driftsstøtte Berg Prestegård"},
{"nummer": 6301 ,"navn": u"Leie lokaler"},
{"nummer": 7410 ,"navn": u"Videre bet medlemskap NKSS"},
{"nummer": 7460 ,"navn": u"Adm. Støtte til NKSS"},
{"nummer": 4200 ,"navn": u"Undergruppemiddag"},
#Vafling (misjons-gruppa)      (UTGÅR)
{"nummer": 4201 ,"navn": u"Sekriteriatet"},
{"nummer": 4202 ,"navn": u"Kjøkkengruppe utgifter"},
{"nummer": 4203 ,"navn": u"Åpenbaringen utgifter"},
{"nummer": 4605 ,"navn": u"T&W utgifter"},
{"nummer": 4700 ,"navn": u"Kollekt ut misjonsprosjekt"},
{"nummer": 4701 ,"navn": u"Kollekt ut annet"},
{"nummer": 4604 ,"navn": u"Detasjamentet"},
{"nummer": 4603 ,"navn": u"Fresh/Fadderopplegg"},
{"nummer": 6862 ,"navn": u"Konferanser deltageravgift"},
{"nummer": 4602 ,"navn": u"Cellegrupper"},
{"nummer": 4601 ,"navn": u"Kostnader Alpha"},
{"nummer": 4230 ,"navn": u"Diverse kontor"},
{"nummer": 8140 ,"navn": u"Rentekostnader"},
{"nummer": 8170 ,"navn": u"Andre finanskostnader og gebyrer"},
{"nummer": 7320 ,"navn": u"PR/program"},
{"nummer": 6540 ,"navn": u"Teknisk utstyr"},
{"nummer": 6860 ,"navn": u"Reisestøtte taler"},
{"nummer": 4600 ,"navn": u"Kostnader arr"},
{"nummer": 6861 ,"navn": u"Reisestøtte medlemmer"},
{"nummer": 6863 ,"navn": u"Internasjonalt besøk"},
{"nummer": 6864 ,"navn": u"Besøk misjonsprosjekt"},
{"nummer": 6865 ,"navn": u"Støtte Hald-studenter"},
{"nummer": 7790 ,"navn": u"Diverse utgifter"},
{"nummer": 8500 ,"navn": u"Ekstraordinær kostnad"},
#Eiendeler, gjeld og egenkapital
{"nummer": 1920 ,"navn": u"Postbanken 0540.08.13398 (Drift TKS)"},
{"nummer": 1010 ,"navn": u"Kontingent neste år"},
{"nummer": 2910 ,"navn": u"Mellomværende TKS/ Medlemmer"},
{"nummer": 2980 ,"navn": u"Skyldig medlemskontigent NKSS"},
{"nummer": 1900 ,"navn": u"Kasse kasserer (kontanter)"},
{"nummer": 1902 ,"navn": u"Kasse åpenbaringen (Kontanter)"},
{"nummer": 1901 ,"navn": u"Kasse tur og weekend"},
{"nummer": 1460 ,"navn": u"T-skjorter (Eiendel uten funksjon)"},
{"nummer": 2050 ,"navn": u"Egenkapital"},
{"nummer": 2981 ,"navn": u"Gaver avsatt misjonspro."},
#Det kommer til å komme til flere bankkontoer

#Ser for meg følgende kontoer foreløpig:

{"nummer": 1923 ,"navn": u"Arrangementer (Deltakeravgift)"},
{"nummer": 1921 ,"navn": u"Givertjeneste"},
{"nummer": 1922 ,"navn": u"Medlemsavgift (Innbetaling medlemmsavgift)"},
{"nummer": 1924 ,"navn": u"T&W (Driftskonto)"},
]

for konto in kontos:
    k = Konto()
    k.nummer = konto['nummer']
    k.tittel = konto['navn']
    k.kontoType = konto['nummer'] // 1000
    k.prosjekt_id = 1
    k.save()
