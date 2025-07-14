import datetime

from .loggers import logger


def format_fusion_ai_response(response: dict) -> str:
    """
    Format the response from Fusion AI into a readable string.
    Args:
        response (dict): The response from Fusion AI.
    Returns:
        str: A formatted string containing the response text,
             entities, and Chat ID.
    """
    if not _check_response_format(response):
        logger.error("Invalid response format from Fusion AI.")
        return "Invalid response format from Fusion AI."
    try:

        data = response
        # Get the response text for introduction
        intro_text = (
            data.get("response", {})
            .get("text", "Business information")
            .replace("[[HIGHLIGHT]]", "**")
            .replace("[[ENDHIGHLIGHT]]", "**")
        )

        # Chat ID
        chat_id = data.get("chat_id", "Unknown Chat ID")

        # Initialize the formatted output
        formatted_output = (
            "# Formatted Business Data for LLM Processing\n\n"
            "## Introduction\n"
            f"{intro_text}\n \n"
            "## Chat ID\n"
            f"{chat_id}\n\n"
        )

        # Check if entities and businesses exist
        businesses = []
        for entity in data.get("entities", []):
            if "businesses" in entity:
                businesses = entity["businesses"]
                break

        logger.debug("Found %d businesses for the query", len(businesses))

        # Process each Business
        for index, business in enumerate(businesses):
            name = business.get("name", "Unknown")
            formatted_output += f"\n## Business {index + 1}: {name}\n"

            # Rating and reviews
            rating = business.get("rating")
            review_count = business.get("review_count")
            price = business.get("price", "")
            if price:
                formatted_output += f"- **Price**: {price}\n"
            else:
                formatted_output += "- **Price**: Not available\n"
            if rating:
                review_info = f"{rating}/5"
                if review_count:
                    review_info += f" ({review_count} reviews)"
                formatted_output += f"- **Rating**: {review_info}\n"

            # Categories
            categories = business.get("categories", [])
            if categories:
                cat_titles = [
                    cat.get("title") for cat in categories if cat.get("title")
                ]
                formatted_output += f"- **Type**: {', '.join(cat_titles)}\n"

            # Location
            location = business.get("location", {})
            if location:
                address_parts = location.get("formatted_address", "").split("\n")
                address = ", ".join(filter(None, address_parts))
                formatted_output += f"- **Location**: {address}\n"

            # Coordinates
            coordinates = business.get("coordinates", {})
            if coordinates:
                lat = coordinates.get("latitude", "")
                lon = coordinates.get("longitude", "")
                if lat and lon:
                    formatted_output += f"- **Coordinates**: {lat}, {lon}\n"
                else:
                    formatted_output += "- **Coordinates**: Not available\n"
            else:
                formatted_output += "- **Coordinates**: Not available\n"

            # URL
            url = business.get("url", "")
            if url:
                formatted_output += f"- **URL**: [View on Yelp]({url})\n"

            # Phone
            phone = business.get("phone", "")
            if phone:
                formatted_output += f"- **Phone**: {phone}\n"

            # Website
            website = business.get("attributes", {}).get("BusinessUrl")
            if website:
                formatted_output += f"- **Website**: {website}\n"

            # Services
            services = []

            if attributes := business.get("attributes", {}):
                formatted_attributes = _format_business_attributes(attributes)
                if formatted_attributes:
                    services.append(formatted_attributes)

            if services:
                formatted_output += (
                    "- **Services and Amenities**: \n  - "
                    + "\n  - ".join(services)
                    + "\n"
                )

            # Contextual Info
            contextual_info = business.get("contextual_info", {})

            # Business hours
            day_wise_business_hours = contextual_info.get("business_hours", [])
            if day_wise_business_hours and len(day_wise_business_hours) > 0:
                formatted_output += "- **Hours**:\n"
                for day in day_wise_business_hours:
                    day_name = day.get("day_of_week", "Unknown")
                    business_hours = day.get("business_hours", [])
                    if business_hours:
                        open_time = business_hours[0].get("open_time", "")
                        close_time = business_hours[0].get("close_time", "")
                        try:
                            open_dt = datetime.datetime.fromisoformat(open_time)
                            close_dt = datetime.datetime.fromisoformat(close_time)
                            open_str = open_dt.strftime("%I:%M %p")
                            close_str = close_dt.strftime("%I:%M %p")
                            formatted_output += (
                                f"  - {day_name}: {open_str} - {close_str}\n"
                            )
                        except ValueError:
                            formatted_output += f"  - {day_name}: Available\n"

            # Overall Review Snippet
            overall_review_snippet = contextual_info.get("review_snippet")
            if overall_review_snippet:
                review_text = overall_review_snippet.replace(
                    "[[HIGHLIGHT]]", "**"
                ).replace("[[ENDHIGHLIGHT]]", "**")
                formatted_output += f"- **Review Highlight**: {review_text}\n"

            # Individual Review Snippets
            review_snippets = contextual_info.get("review_snippets", [])
            if review_snippets:
                formatted_output += "- **Customer Reviews**:\n"
                for snippet in review_snippets:
                    rating = snippet.get("rating")
                    comment = snippet.get("comment", "No comment.")
                    # Replace highlight markers with markdown bold
                    comment = comment.replace("[[HIGHLIGHT]]", "**").replace(
                        "[[ENDHIGHLIGHT]]", "**"
                    )
                    if rating:
                        formatted_output += f"  - Rating: {rating}/5\n"
                        formatted_output += f"    {comment}\n"
                    else:
                        formatted_output += f"  - {comment}\n"

            # Photos
            photos = contextual_info.get("photos", [])
            if photos:
                formatted_output += "- **Photos**:\n"
                for photo in photos:
                    photo_url = photo.get("original_url")
                    if photo_url:
                        formatted_output += f"  - {photo_url}\n"

            # Description from summaries
            summaries = business.get("summaries", {})
            long_summary = summaries.get("long", "")
            short_summary = summaries.get("short", "")
            description = long_summary or short_summary
            if description:
                formatted_output += f"- **Description**: {description}\n"

        logger.debug("Formatted output for LLM:\n%s", formatted_output)
        return formatted_output
    except (KeyError, TypeError, ValueError) as e:
        logger.error(e)
        return "Unable to fetch data from Yelp. Invalid response format."


def _check_response_format(response: dict) -> bool:
    """
    Check if the response from Fusion AI is in the expected format.
    Args:
        response (dict): The response from Fusion AI.
    Returns:
        bool: True if the response is in the expected format, False otherwise.
    """
    return (
        isinstance(response, dict)
        and "response" in response
        and isinstance(response["response"], dict)
        and "text" in response["response"]
        and "entities" in response
        and "chat_id" in response
    )


def _format_business_attributes(attributes: dict) -> str:
    """
    Format the business attributes for display.
    Args:
        attributes (dict): The business attributes.
    Returns:
        str: The formatted attributes.
    """
    if not attributes:
        return ""

    formatted_attributes = []

    # Simple boolean checks with user-friendly names
    boolean_checks = {
        "BusinessAcceptsAndroidPay": "Accepts Android Pay",
        "BusinessAcceptsApplePay": "Accepts Apple Pay",
        "GenderNeutralRestrooms": "Gender-Neutral Restrooms",
        "BusinessOpenToAll": "Open to All",
        "PokestopNearby": "Pokestop Nearby",
        "BikeParking": "Bike Parking Available",
        "BusinessAcceptsBitcoin": "Accepts Bitcoin",
        "BusinessAcceptsCreditCards": "Accepts Credit Cards",
        "Caters": "Catering Available",
        "Corkage": "Corkage Available",
        "DogsAllowed": "Dog-friendly",
        "DriveThru": "Drive-Thru Available",
        "FlowerDelivery": "Flower Delivery Available",
        "GoodForKids": "Good for Kids",
        "HappyHour": "Happy Hour Specials",
        "HasTV": "Has TV",
        "OffersMilitaryDiscount": "Offers Military Discount",
        "OnlineReservations": "Online Reservations",
        "Open24Hours": "Open 24 Hours",
        "PlatformDelivery": "Platform Delivery",
        "RestaurantsCounterService": "Counter Service",
        "RestaurantsDelivery": "Offers Delivery",
        "RestaurantsGoodForGroups": "Good for Groups",
        "RestaurantsReservations": "Takes Reservations",
        "RestaurantsTableService": "Table Service",
        "RestaurantsTakeOut": "Offers Takeout",
        "WheelchairAccessible": "Wheelchair Accessible",
    }

    for key, text in boolean_checks.items():
        if attributes.get(key) is True:
            formatted_attributes.append(f"{text} ✓")

    # String value attributes
    if alcohol := attributes.get("Alcohol"):
        if alcohol != "none":
            alc_str = alcohol.replace("_", " ").title()
            formatted_attributes.append(f"Alcohol: {alc_str}")

    if noise := attributes.get("NoiseLevel"):
        noise_str = noise.replace("_", " ").title()
        formatted_attributes.append(f"Noise Level: {noise_str}")

    if attire := attributes.get("RestaurantsAttire"):
        formatted_attributes.append(f"Attire: {attire.title()}")

    if wifi := attributes.get("WiFi"):
        if wifi != "no":
            formatted_attributes.append(f"WiFi: {wifi.title()}")
        else:
            formatted_attributes.append("WiFi: Not Available")

    # Nested Ambience
    ambience = attributes.get("Ambience", {})
    if isinstance(ambience, dict):
        active_ambience = [
            key.title() for key, value in ambience.items() if value is True
        ]
        if active_ambience:
            amb_str = ", ".join(active_ambience)
            formatted_attributes.append(f"Ambience: {amb_str}")

    # Nested BusinessParking
    parking = attributes.get("BusinessParking", {})
    if isinstance(parking, dict):
        available_parking = [
            key.title() for key, value in parking.items() if value is True
        ]
        if available_parking:
            park_str = ", ".join(available_parking)
            formatted_attributes.append(f"Parking: {park_str}")
        else:
            formatted_attributes.append("Parking: Not specified")

    # BYOB/Corkage
    if attributes.get("BYOB") is True:
        formatted_attributes.append("BYOB ✓")
    if byob_corkage := attributes.get("BYOBCorkage"):
        if byob_corkage == "yes_corkage":
            formatted_attributes.append("Corkage for BYOB: Yes")
        elif byob_corkage == "yes_free":
            formatted_attributes.append("Corkage for BYOB: Free")
        elif byob_corkage != "no":
            formatted_attributes.append(f"BYOB Corkage: {byob_corkage}")

    # GoodForMeal
    good_for_meal = attributes.get("GoodForMeal", {})
    if isinstance(good_for_meal, dict):
        suitable_meals = [key.title() for key, value in good_for_meal.items() if value]
        if suitable_meals:
            meals_str = ", ".join(suitable_meals)
            formatted_attributes.append(f"Good for: {meals_str}")

    # Price Range
    if price_range := attributes.get("RestaurantsPriceRange2"):
        formatted_attributes.append(f"Price Range: {'$' * int(price_range)}")

    # About This Biz
    if history := attributes.get("AboutThisBizHistory"):
        hist_text = history[:150] + "..." if len(history) > 150 else history
        formatted_attributes.append(f"History: {hist_text}")
    if specialties := attributes.get("AboutThisBizSpecialties"):
        formatted_attributes.append(f"Specialties: {specialties}")
    if year_established := attributes.get("AboutThisBizYearEstablished"):
        formatted_attributes.append(f"Established: {year_established}")

    # Menu URL
    if menu_url := attributes.get("MenuUrl"):
        if menu_url.startswith("http"):
            formatted_attributes.append(f"Menu: [View Menu]({menu_url})")

    return "\n  - ".join(formatted_attributes)
