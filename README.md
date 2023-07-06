# ADAC-Car-Seat-Safety-Ratings

ADAC is a vehicle insurance company that tests the safety of car seats to standards that far exceed the standard EU regulations.

You can browse the results here: [https://www.adac.de/...](https://www.adac.de/rund-ums-fahrzeug/ausstattung-technik-zubehoer/kindersitze/kindersitztest/)

Unfortunately, you can only filter the results by a few categories. This script remedies that.

Scrapes all child car seats tested by adac.de and outputs them to a DataFrame and/or Excel. This allows you to filter by any tracked category, not only the few parameters allowed by ADAC.

-------------

Tracked categories:
- Name
- URL
- Brand
- Model
- Description
- Summary
- Price
- Test Year
- Current
- Full Rating
- Security Rating
- Security Strengths
- Security Weaknesses
- Operation Rating
- Operation Strengths
- Operation Weaknesses
- Ergonomy Rating
- Ergonomy Strengths
- Ergonomy Weaknesses
- Pollutants Rating
- Pollutants Strengths
- Pollutants Weaknesses
- Processing and Cleaning Rating
- Processing and Cleaning Strengths
- Processing and Cleaning Weaknesses
- Age Class
- Approved Child Weight
- Child Height From
- Child Height To
- Backward Facing Option
- Forward Facing Option
- Horizontal Transport
- Isofix
- Impact Shield
- Two-point Belt
- Seat Weight
- Montage Notes
