Das Hauptziel dieser Website ist es, eine Online-Verbindung zwischen Immobilienverkäufern und -käufern zu ermöglichen. Derzeit bietet die Website die Möglichkeit, hochgeladene Häuser zu besichtigen und Immobilien nach Anmeldung hochzuladen. Der Upload-Prozess funktioniert so, dass der Benutzer festlegt, ob die Immobilie zum Verkauf oder zur Miete angeboten wird, und basierend darauf den Preis oder die monatliche Miete, die Fläche und die Adresse der Immobilie auf der Karte angibt. Angemeldete Benutzer können auch ein Haus zu ihrer Favoritenliste hinzufügen.

Auf dieser Website erfolgt die Suche hauptsächlich anhand des Standorts. Das bedeutet, dass der Benutzer eine Adresse eingeben kann, und basierend auf der Eingabe werden Adressen aus der Datenbank als Suchvorschläge angezeigt. Anschließend kann der Benutzer einen der Suchvorschläge auswählen, und alle verfügbaren Häuser in diesem Gebiet werden angezeigt. Es ist auch möglich, diese Adressen auf der Karte zu sehen, damit der Benutzer die allgemeine Lage des Hauses in der Stadt erkennen kann. Der Benutzer kann seine Suche weiter eingrenzen, indem er Filter wie Preisspanne, Fläche oder ob die Häuser zum Verkauf oder zur Miete angeboten werden, verwendet. Darüber hinaus besteht die Möglichkeit, dass angemeldete Benutzer miteinander chatten können.

Zusätzlich bietet die Seite auch eine Preisprognose durch eine Polynomialregression. Benutzer können die Art des Eigentums, die Adresse des Eigentums auf der Karte und den gewünschten Zeitraum festlegen. Basierend auf diesen Informationen wird der Preis für die angegebene Zeitspanne berechnet. Das Dataset für dieses Modell liegt in einer CSV-Datei vor. In diesem Datensatz habe ich jede 20 km² als eine Fläche definiert und die Breitengrade und Längengrade des Zentrums jeder Fläche festgelegt. Ich habe auch den ungefähren Durchschnittspreis für verschiedene Arten des Eigentums in jeder Fläche für jedes Jahr von 2010 bis 2020 festgelegt. Dann werden die festgelegten Breiten- und Längengrade der vom Benutzer angegebenen Adresse mit den Breiten- und Längengraden jeder Fläche verglichen, um herauszufinden, in welcher Fläche sich diese Adresse befindet. Basierend auf der Art des Eigentums und den Durchschnittspreisen in dieser Fläche wird der Preis prognostiziert. Dieses Dataset wird kontinuierlich durch die Daten der auf der Website eingestellten Immobilien erweitert.