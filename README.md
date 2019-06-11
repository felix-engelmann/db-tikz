# db-tikz

This is a small project to generate nice journey path traveled with Deutsche Bahn.
It can process real time updates and intermediate stops.
The data is provided via a json file and tikz code is generated, which can be included in any document. A standalone minimal wrapper can be used to generate standalone pdfs.

## Usage

Please provide your trip in a json file, e.g. trip.json.
There should be a list of `legs` each with a `departure` and `arrival` key.
From the second leg on, the departure station can be omitted. Real time information is provided with the `actual` key. Any delay greater than 5 minutes is colored red.

A train can display a list of intermediate stations with name and time or times.
If a departure time is provided, both times are displayed.

## Example

The trip.json provides the following output:

![Journey Image](trip.png?raw=true "Journey")