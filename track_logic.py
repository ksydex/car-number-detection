import re
import numpy
from detection_level import DetectionLevel


def check_numbers_overlaps(labls_cords: dict, detection_level=DetectionLevel.LICENSE_PLATE) -> list:

    """
    Check each number's BB and correlate it with car's BB

    return: list - the list has following structure [
        [(number's cords), (car's cords), 'car_type'],
        [(number's cords), (car's cords), 'car_type'],
        ...
        ]
    
    If detection_level is CAR_ONLY, it will also include cars without plates:
        [[None, (car's cords), 'car_type'], ...]
    """

    new_cars = []
    processed_vehicles = set()

    # First process cars with license plates
    for number in labls_cords["numbers"]:

        for car in labls_cords["cars"]:
            # check if number's bounding box fully overlaps car's
            if (car[0] <= number[0] <= number[2] <= car[2]) and (
                car[1] <= number[1] <= number[3] <= car[3]
            ):
                new_cars.append([number, car, "car"])
                # Track which vehicles have been processed
                processed_vehicles.add(tuple(car))

        for car in labls_cords["trucks"]:
            # check if number's bounding box fully overlaps car's
            if (car[0] <= number[0] <= number[2] <= car[2]) and (
                car[1] <= number[1] <= number[3] <= car[3]
            ):
                new_cars.append([number, car, "truck"])
                processed_vehicles.add(tuple(car))

        for car in labls_cords["busses"]:
            # check if number's bounding box fully overlaps car's
            if (car[0] <= number[0] <= number[2] <= car[2]) and (
                car[1] <= number[1] <= number[3] <= car[3]
            ):
                new_cars.append([number, car, "bus"])
                processed_vehicles.add(tuple(car))

    # If we're showing all cars, add those without license plates
    if detection_level == DetectionLevel.CAR_ONLY:
        # Add remaining cars without plates
        for car in labls_cords["cars"]:
            if tuple(car) not in processed_vehicles:
                new_cars.append([None, car, "car"])
        
        # Add remaining trucks without plates
        for truck in labls_cords["trucks"]:
            if tuple(truck) not in processed_vehicles:
                new_cars.append([None, truck, "truck"])
                
        # Add remaining buses without plates
        for bus in labls_cords["busses"]:
            if tuple(bus) not in processed_vehicles:
                new_cars.append([None, bus, "bus"])

    return new_cars

