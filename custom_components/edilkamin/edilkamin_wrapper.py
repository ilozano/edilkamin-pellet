class EdilkaminWrapper(object):

    @staticmethod
    def get_power_status(data):
        return data.get("status").get("commands").get("power")

    @staticmethod
    def get_airkare_status(data):
        return data.get("status").get("flags").get("is_airkare_active")

    @staticmethod
    def get_relax_status(data):
        return data.get("status").get("flags").get("is_relax_active")

    @staticmethod
    def get_status_tank(data):
        return data.get("status").get("flags").get("is_pellet_in_reserve")

    @staticmethod
    def get_fan_1_speed(data):
        return data.get("status").get("fans").get("fan_1_speed")

    @staticmethod
    def get_target_temperature(data):
        return data.get("nvm").get("user_parameters").get("enviroment_1_temperature")

    @staticmethod
    def get_actual_power(data):
        return data.get("status").get("state").get("actual_power")

    @staticmethod
    def get_alarms(data):
        """Get the target temperature."""
        alarms_info = data.get("nvm").get("alarms_log")
        index = alarms_info.get("index")
        alarms = []

        for i in range(index):
            alarms.append(alarms_info.get("alarms")[i])

        return alarms

    @staticmethod
    def get_nb_alarms(data):
        """Get the target temperature."""
        return data.get("nvm").get("alarms_log").get("index")

    @staticmethod
    def get_temperature(data):
        """Get the target temperature."""
        return data.get("status").get("temperatures").get("enviroment")
