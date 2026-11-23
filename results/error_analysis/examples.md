# Error analysis (test split)

## qwen3_asr_0.6b

Substitutions: 2090 (Turkish letter 41, suffix 764, other 1285); deletions 373; insertions 194; clips wrong only because of spacing: 65.

**turkish_letter**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_30603572 | Dışardayken hali vakti yerinde, iki karılı olduğunu söylediği halde, senelerden beri arayan, soran yoktu. | Dışarıdakı halı vakti yerinde, iki karılı olduğunu söylediği halde senelerden beri arayan soran yoktu. | hali -> halı |
| common_voice_tr_48139584 | Bu görevinde gösterdiği yetenek ve cesaretinden ötürü Sovyetler Birliği Kahramanı unvanı verildi. | Bu görevinde gösterdiği yetenek ve cesaretinden ötürü Sovyetler Birliği kahramanı ünvanı verildi. | unvanı -> ünvanı |
| common_voice_tr_30603569 | Gönül bir sırça saraydır, kırılırsa yapılmaz. | Gönül bir sırca saraydır. Kırılırsa yapılmaz. | sırça -> sırca |
| common_voice_tr_39749517 | Sultanbey de bundan sonra Cihan'la evlenmeye hazırdır. | Sultan Bey de bundan sonra Cihan'la evlenmeye hazırdir. | hazırdır -> hazırdir |
| common_voice_tr_19878362 | Kosor bekâr bir anne ve iki adet şiir kitabı var. | Kosör Beker bir anne ve iki adet şiir kitabı var. | kosor -> kosör |

**suffix**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17857535 | Seçimlerde usulsüzlük bildirilmedi. | Seçimlere usulsüzlik bildirilmedi. | seçimlerde -> seçimlere |
| common_voice_tr_17857535 | Seçimlerde usulsüzlük bildirilmedi. | Seçimlere usulsüzlik bildirilmedi. | usulsüzlük -> usulsüzlik |
| common_voice_tr_42457711 | Berlin Eyalet Başbakanı için çalıştı. | Berdin Eyalet Başbakanı için çalıştı. | berlin -> berdin |
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. | Proje 2012 yılında hizmete girebilir. | girebililr -> girebilir |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | Borlonun kırsa kalına mı kandın tatlı diline mi? | borlunun -> borlonun |

**other**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | Sanatta her şey kendi yerine düşer. | herşey -> şey |
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. | Proje 2012 yılında hizmete girebilir. | iki -> 2012 |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | Borlonun kırsa kalına mı kandın tatlı diline mi? | sakalına -> kalına |
| common_voice_tr_17343291 | Oruçtan sonra Sırplar et yemekleri yiyorlar. | Oruçtan sonra sıplar et yemeklerini yiyorlar. | sırplar -> sıplar |
| common_voice_tr_28906732 | Gayrı ölesiye kadar gene böyle tarlada bağda çalışacağız ha! | Gayrı ölesiye kadar gene böyle tarla da bağda çalışacağız ha. | tarlada -> da |

**deletion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. | Proje 2012 yılında hizmete girebilir. | missing: bin on iki |
| common_voice_tr_36374474 | Kırk yedi. | Küçüydi. | missing: yedi |
| common_voice_tr_33097699 | Haydi, deniz kenarına bir yere gidip dolaşalım… | Haydi dediskenarına bir yere gidip dolaşalım. | missing: kenarına |
| common_voice_tr_21318048 | Yarışmaya yirmi yedi ülkeden şarkıcılar katıldı. | Yarışmaya 27 ülkeden şarkıcılar katıldı. | missing: yedi |
| common_voice_tr_39927099 | Genellikle organik bileşiklerin elektron iyonizasyon kütle spektrometresinden tanımlanması için kullanılır. | Genellikle organik bileşiklerin elektron iyonizasyon kültülspektrometresinden tanımlanması için kullanılır. | missing: spektrometresinden |

**insertion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | Sanatta her şey kendi yerine düşer. | extra: her |
| common_voice_tr_28906732 | Gayrı ölesiye kadar gene böyle tarlada bağda çalışacağız ha! | Gayrı ölesiye kadar gene böyle tarla da bağda çalışacağız ha. | extra: tarla |
| common_voice_tr_31657558 | Gerçekçi olalım. | Gerçek şey olalım. | extra: gerçek |
| common_voice_tr_26968913 | Kımıldayın. | Kamil Dayan | extra: kamil |
| common_voice_tr_18395538 | On milletvekili çekimser kaldı. | On millet vekili çekim serk aldı. | extra: millet vekili |

## seda_rnnt

Substitutions: 1452 (Turkish letter 9, suffix 606, other 837); deletions 265; insertions 175; clips wrong only because of spacing: 68.

**turkish_letter**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_24376035 | Projeyi iki hükümet de finanse edecek. | projeyi iki hükumet de finanse edecek | hükümet -> hükumet |
| common_voice_tr_21318096 | Bu uygulama ilk kez yapılmiyor. | bu uygulama ilk kez yapılmıyor | yapılmiyor -> yapılmıyor |
| common_voice_tr_39927102 | Bu kurulan partinin ismi daha sonra Toplumcu Kurtuluş Partisi Yeni Güçler olarak değiştirildi. | bu kurulan partının ismi daha sonra toplumcu kurtlu partisi yeni güçler olarak değiştirildi | partinin -> partının |
| common_voice_tr_20557338 | Kosova hükümeti de sert tepki verdi. | kosova hükumeti de sert tepki vardı | hükümeti -> hükumeti |
| common_voice_tr_43561326 | Açı veya hava sıcaklıkları gibi farklı birçok alanda dereceyi ifade etmek için bu simge kullanılır. | acı veya hava sıcaklıkları gibi farklı birçok alanda dereceyi ifade etmek için bu simge kullanılır | açı -> acı |

**suffix**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. | proje iki bin on iki yılında hizmete girebilir | girebililr -> girebilir |
| common_voice_tr_18270288 | AB temsilcileri haberi memnuniyetle karşıladılar. | ab temsilcileri haberin memnuniyetle karşıladılar | haberi -> haberin |
| common_voice_tr_39730670 | Sıvı bir formülasyon da mevcuttur. | sıvı bir formülasyonda mevcuttur | formülasyon -> formülasyonda |
| common_voice_tr_30674459 | İkisinin de gözleri yaşarmıştı. | ikisini de gözleri yaşarmıştı | ikisinin -> ikisini |
| common_voice_tr_38146996 | Burada her şey yolunda. | burada her şeyin yolunda | şey -> şeyin |

**other**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | sanatta her şey kendi yerine düşer | herşey -> şey |
| common_voice_tr_28906732 | Gayrı ölesiye kadar gene böyle tarlada bağda çalışacağız ha! | gayrı öğlesiye kadar gene böyle tarlada bağda çalışacağız ha | ölesiye -> öğlesiye |
| common_voice_tr_30603572 | Dışardayken hali vakti yerinde, iki karılı olduğunu söylediği halde, senelerden beri arayan, soran yoktu. | dışarıdayken hali vakti yerinde iki karılı olduğunu söylediği halde senelerden beri arayan soran yoktu | dışardayken -> dışarıdayken |
| common_voice_tr_38406381 | Burası müşterilerini savmış bir gazinoya benziyordu. | burası müşterilerini sarmış bir gazinoya benziyordu | savmış -> sarmış |
| common_voice_tr_43603505 | Ayrıca kurulan Kızıl Muhafızlar kısa süre sonra sosyal-demokrat güvenlik birlikleri içinde eridiler. | ayrıca kurulan kızıl muhafızlar kısa süre sonra sosyal demokrat güvenlik birlikleri içinde er ucu da | eridiler -> da |

**deletion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_39730670 | Sıvı bir formülasyon da mevcuttur. | sıvı bir formülasyonda mevcuttur | missing: da |
| common_voice_tr_40341037 | Batı yakası sahilinin eşcinsel içerikli ilk yazılı eserlerinin ilk dalgasının önemli yazarlarındandır. | batı hın seyretti ilk yazılısırların tavgasının önünde yazarlarındandır | missing: eşcinsel içerikli |
| common_voice_tr_40341037 | Batı yakası sahilinin eşcinsel içerikli ilk yazılı eserlerinin ilk dalgasının önemli yazarlarındandır. | batı hın seyretti ilk yazılısırların tavgasının önünde yazarlarındandır | missing: dalgasının önemli |
| common_voice_tr_36701273 | Bu adreste alt yapı görünmüyor daha önce internet kullanımı sağlamış mıydınız? | bu adreste altyapı görünmüyor daha önce internet kullanını sağlamış mıydınız | missing: yapı |
| common_voice_tr_39769931 | Seri şu anda her biri iki segment içeren kırk yarım saatlik bölüm için üretiliyor. | serin şu anda her biriksekmentçeren kırık yerim ya saatlik bölüm için üretiliyor | missing: kırk yarım |

**insertion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | sanatta her şey kendi yerine düşer | extra: her |
| common_voice_tr_43603505 | Ayrıca kurulan Kızıl Muhafızlar kısa süre sonra sosyal-demokrat güvenlik birlikleri içinde eridiler. | ayrıca kurulan kızıl muhafızlar kısa süre sonra sosyal demokrat güvenlik birlikleri içinde er ucu da | extra: er ucu |
| common_voice_tr_38146998 | Sağol, kalsın. | sağ ol kalsın | extra: sağ |
| common_voice_tr_18290489 | İki madende iki bin beş yüzden fazla kişi çalışıyor. | iki maden de iki bin beş yüzden fazla kişi çalışıyor | extra: maden |
| common_voice_tr_23660893 | Hayatta küçük şeyleri kovalıyor ve yine küçük şeyler için birbirimizi incitiyoruz. | için hatta küçük şeyler için birbiri bir şeyleri kovalıyor ve yine küçük şeyler için birbirimizi inciltiyoruz | extra: için |

## wav2vec2_xlsr_tr

Substitutions: 3081 (Turkish letter 34, suffix 1072, other 1975); deletions 434; insertions 472; clips wrong only because of spacing: 107.

**turkish_letter**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_27356116 | Hayır, onu görmemiştim. | hayir onu görmem iştim | hayır -> hayir |
| common_voice_tr_26084120 | Güreşçi olarak yetenekleri sınırlıydı. | dreşçi olarak hetenekleri sınırliydı | sınırlıydı -> sınırliydı |
| common_voice_tr_37181599 | Suyun yanından geçip gidermiş, bir de ne görsün: | suyunyanından geçip lidermiş bir de ne gorsun | görsün -> gorsun |
| common_voice_tr_43561582 | Çözülen kireç taşlarındaki kırıklar genişlemiş ve yer altından geçen bir su kanalı oluşmuştur. | çözine kileç taşırarındaki kırıklar genişlemiş ve yer altından gecen bir sukanalı oluşmuştur | geçen -> gecen |
| common_voice_tr_31657557 | Doğruyu söyle. | doğruğu soyle | söyle -> soyle |

**suffix**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | sanatda herşey kendi yerine düşer | sanatta -> sanatda |
| common_voice_tr_42457711 | Berlin Eyalet Başbakanı için çalıştı. | berden eyalet başbakanı için çalıştı | berlin -> berden |
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. | proje iki bin on iki yılında hizmete girebilir | girebililr -> girebilir |
| common_voice_tr_28906732 | Gayrı ölesiye kadar gene böyle tarlada bağda çalışacağız ha! | gair öylesiye kadar gene böyle tarnada bağda çalışacağa saha | çalışacağız -> çalışacağa |
| common_voice_tr_48139584 | Bu görevinde gösterdiği yetenek ve cesaretinden ötürü Sovyetler Birliği Kahramanı unvanı verildi. | bu görevinde gösterdiy yetenek ve cezaretinden ötürü soviyetler birliği kahramanı iumvanı verildi | gösterdiği -> gösterdiy |

**other**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17857535 | Seçimlerde usulsüzlük bildirilmedi. | seçimlerde ulusözsözlük bildirilmedi | usulsüzlük -> ulusözsözlük |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk saka una mı kandın tatla d iline mi | borlunun -> kırk |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk saka una mı kandın tatla d iline mi | kır -> saka |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk saka una mı kandın tatla d iline mi | sakalına -> una |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk saka una mı kandın tatla d iline mi | tatlı -> d |

**deletion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_30773194 | Onun için şimdi denize atılmış görünüp satılan portakallarını o boşaltmıyordu. | onun için şimdi denizatılmış görünüp satılam portakallarına oboş altmıyordu | missing: atılmış |
| common_voice_tr_33097699 | Haydi, deniz kenarına bir yere gidip dolaşalım… | haylinderi iskenarrına bir yere gilip doluşalım | missing: kenarına |
| common_voice_tr_39730670 | Sıvı bir formülasyon da mevcuttur. | sıvı bir formulasyonda mayacutdur | missing: mevcuttur |
| common_voice_tr_28090057 | Maria bu akşam garip denilecek kadar çok neşeliydi. | maria bu alkışam galivlenilecek kadar çok nüşeliydi | missing: denilecek |
| common_voice_tr_30674390 | Lanet oIsun! | lanetoz | missing: oısun |

**insertion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk saka una mı kandın tatla d iline mi | extra: borlonun |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk saka una mı kandın tatla d iline mi | extra: tatla |
| common_voice_tr_19596422 | Romanya bin icat sundu. | romanya bin icat sundu nn | extra: nn |
| common_voice_tr_30674459 | İkisinin de gözleri yaşarmıştı. | i kisinin de gözleri yaşarmıştı | extra: i |
| common_voice_tr_29944231 | Ölüydü. | ölü güttü | extra: ölü |

## wav2vec2_xlsr_tr_finetuned

Substitutions: 2875 (Turkish letter 28, suffix 1161, other 1686); deletions 488; insertions 202; clips wrong only because of spacing: 78.

**turkish_letter**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_37181599 | Suyun yanından geçip gidermiş, bir de ne görsün: | suun yanından geçip gidermiş birde ne görsun | görsün -> görsun |
| common_voice_tr_43561582 | Çözülen kireç taşlarındaki kırıklar genişlemiş ve yer altından geçen bir su kanalı oluşmuştur. | çözüne kileç taşrarındaki kırıklar genişlemiş ve yer altından gecen bir sukanalı oluşmuştur | geçen -> gecen |
| common_voice_tr_37179808 | Bilhassa hayatı bu kadarcık olsun gördükten sonra yeknesak mesai seni boğar. | bil hassa hayatı bu kadarçık olsun yördükten sonra yeknesak mesajesini bu ar | kadarcık -> kadarçık |
| common_voice_tr_17425667 | Birçok yorumcu da aynı görüşü dile getirdi. | birçok yörümcu da aynı görüşdile getirdi | yorumcu -> yörümcu |
| common_voice_tr_18200069 | Kosova'da altı hafta önce nüfus sayımı yapıldı. | kosovada altı hafta önce nüfüs sayımı yapıldı | nüfus -> nüfüs |

**suffix**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | sanatda herşey kendi yerne düşer | sanatta -> sanatda |
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. | sanatda herşey kendi yerne düşer | yerine -> yerne |
| common_voice_tr_42457711 | Berlin Eyalet Başbakanı için çalıştı. | berden eyalet başbakanı için çalıştı | berlin -> berden |
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. | proje iki bin on iki yılında hizmete girebilir | girebililr -> girebilir |
| common_voice_tr_28906732 | Gayrı ölesiye kadar gene böyle tarlada bağda çalışacağız ha! | gair öylesiye kadar gene böyle tarnıda bağda çalışacağı sah | çalışacağız -> çalışacağı |

**other**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17857535 | Seçimlerde usulsüzlük bildirilmedi. | seçimlerde ulsözsüzlük bildirilmedi | usulsüzlük -> ulsözsüzlük |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk sakağ una mı kandın tatla d iline mi | borlunun -> kırk |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk sakağ una mı kandın tatla d iline mi | kır -> sakağ |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk sakağ una mı kandın tatla d iline mi | sakalına -> una |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk sakağ una mı kandın tatla d iline mi | tatlı -> d |

**deletion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_30773194 | Onun için şimdi denize atılmış görünüp satılan portakallarını o boşaltmıyordu. | onun için şimdi denizatılmış görünüp satılam portakallarına oboş altmıyordu | missing: atılmış |
| common_voice_tr_33097699 | Haydi, deniz kenarına bir yere gidip dolaşalım… | haylider isken arına biryere gidip doluşalım | missing: yere |
| common_voice_tr_28090057 | Maria bu akşam garip denilecek kadar çok neşeliydi. | mariya bu alkışam galiblenilecek kadar çok nışeliydi | missing: denilecek |
| common_voice_tr_39591625 | Saray kayıtlarında buna Ak Ağalar başı' da deniyordu. | saray kayıtlarında buna ak ağlar başıda deniyordu | missing: da |
| common_voice_tr_40341037 | Batı yakası sahilinin eşcinsel içerikli ilk yazılı eserlerinin ilk dalgasının önemli yazarlarındandır. | batyakıssailine de hintel ceretti bilk yazı ezerlenin ilk albasını nönünde yazarlarındandır | missing: eserlerinin |

**insertion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk sakağ una mı kandın tatla d iline mi | extra: borlonun |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? | borlonun kırk sakağ una mı kandın tatla d iline mi | extra: tatla |
| common_voice_tr_31657558 | Gerçekçi olalım. | garçekşi ol alın | extra: garçekşi |
| common_voice_tr_36374464 | Bunun niçin böyle yapıldığını size söylemediler mi? | bunun ni için böyle yapıldığını sizi söylemediler mi | extra: ni |
| common_voice_tr_39749519 | Bıyık Abdullah öldükten sonra Paşa dağının üzerine kurulu olan karargâh epey bir zaman devam etmiştir. | bıyı kaptullah öldükten sonra paşadağının üzerine kurlu olan karar gah epey bir zaman devam etmişter | extra: karar |

## whisper_small

Substitutions: 2219 (Turkish letter 29, suffix 707, other 1483); deletions 396; insertions 283; clips wrong only because of spacing: 67.

**turkish_letter**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_48139584 | Bu görevinde gösterdiği yetenek ve cesaretinden ötürü Sovyetler Birliği Kahramanı unvanı verildi. |  Bu görevinde gösterdiği yetenek ve cesaretinden ötürü Sovyetler Birliği Kahramanı Ünvanı verildi. | unvanı -> ünvanı |
| common_voice_tr_39749519 | Bıyık Abdullah öldükten sonra Paşa dağının üzerine kurulu olan karargâh epey bir zaman devam etmiştir. |  Biyik Abdullah öldükten sonra Paşa'dan üzerine kuru olan Karargah epey bir zaman devam etmişler. | bıyık -> biyik |
| common_voice_tr_36374476 | Akademi'ye yayıldı, hatta bazı çabuk tesirler göstermekte de gecikmedi. |  Akademiye yayıldı. Hatta bazı çabuk tesirler göstermekte de geçikmedi. | gecikmedi -> geçikmedi |
| common_voice_tr_37900169 | Kısa ökçeli kahverengi iskarpinleri kaldırımlarda maharetle sekiyordu. |  kısa ökceli kahverengi iskarpinleri kaldırımlarda maharetle sekiyordu. | ökçeli -> ökceli |
| common_voice_tr_21318096 | Bu uygulama ilk kez yapılmiyor. |  Bu uygulama ilk kez yapılmıyor. | yapılmiyor -> yapılmıyor |

**suffix**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. |  Projey 2012 yılında hizmete girebilir. | proje -> projey |
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. |  Projey 2012 yılında hizmete girebilir. | girebililr -> girebilir |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? |  Borlon'un kırk sakalına mı kendin? Tatlı diline mi? | borlunun -> borlonun |
| common_voice_tr_38113334 | Borlunun kır sakalına mı kandın, tatlı diline mi? |  Borlon'un kırk sakalına mı kendin? Tatlı diline mi? | kır -> kırk |
| common_voice_tr_17343291 | Oruçtan sonra Sırplar et yemekleri yiyorlar. |  Oruçtan sonra sıplar et yemeklerini yiyorlar. | yemekleri -> yemeklerini |

**other**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. |  Sanatla her şey kendi yerine düşer. | sanatta -> her |
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. |  Sanatla her şey kendi yerine düşer. | herşey -> şey |
| common_voice_tr_17857535 | Seçimlerde usulsüzlük bildirilmedi. |  seçimlerde o söz sözlük bildirilmedi. | usulsüzlük -> sözlük |
| common_voice_tr_42457711 | Berlin Eyalet Başbakanı için çalıştı. |  Berlin Eyerlet Başbakanı için çalıştı. | eyalet -> eyerlet |
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. |  Projey 2012 yılında hizmete girebilir. | iki -> 2012 |

**deletion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_17639212 | Proje iki bin on iki yılında hizmete girebililr. |  Projey 2012 yılında hizmete girebilir. | missing: bin on iki |
| common_voice_tr_21318048 | Yarışmaya yirmi yedi ülkeden şarkıcılar katıldı. |  Yerişmeye 27 ülkeden şarkıcılar katıldı. | missing: yedi |
| common_voice_tr_39591625 | Saray kayıtlarında buna Ak Ağalar başı' da deniyordu. |  Saray kayıtlarında buna ak ağalar başıda deniyordu. | missing: da |
| common_voice_tr_19593436 | Projenin değeri yaklaşık altı yüz elli bin avro. |  Projenin değeri yaklaşık 650 bin Avro. | missing: yüz elli |
| common_voice_tr_37181567 | Acı bana. |  Acıbana | missing: bana |

**insertion**

| Clip | Reference | Hypothesis | Error |
|---|---|---|---|
| common_voice_tr_18137605 | Sanatta herşey kendi yerine düşer. |  Sanatla her şey kendi yerine düşer. | extra: sanatla |
| common_voice_tr_17857535 | Seçimlerde usulsüzlük bildirilmedi. |  seçimlerde o söz sözlük bildirilmedi. | extra: o söz |
| common_voice_tr_29944231 | Ölüydü. |  Ölü de | extra: ölü |
| common_voice_tr_26968913 | Kımıldayın. |  Kamil dayın. | extra: kamil |
| common_voice_tr_40341037 | Batı yakası sahilinin eşcinsel içerikli ilk yazılı eserlerinin ilk dalgasının önemli yazarlarındandır. |  Batıya Kısa haliyle de şimdiki çerikli bir ilk yazıl eserlerinin ilk dalgasının önünde yazarlarındandır. | extra: batıya kısa |

