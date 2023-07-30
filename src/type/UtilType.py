from enum import Enum


class UtilType(Enum):
    """
    UtilType is an enum for representing the type of available utils
    
    Option:
        - `ftw`: go-ftw
        - `locust`: locust
        - `cAdvisor`: cAdvisor
        - `eBFF`: eBFF
    """
    ftw = "ftw",
    locust = "locust",
    cAdvisor = "cAdvisor",
    
    # @TODO: impl
    eBFF = "eBFF"