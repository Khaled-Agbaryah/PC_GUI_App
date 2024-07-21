class logger:
    def __init__(self, log_file_path = "", auto_save = True) -> None:
        self.__messages = []
        self.__log_text = ""
        self.__file_path = log_file_path
        self.__auto_save = auto_save

    def add_message(self, msg: str) -> None:
        self.__messages.append(msg)
        self.__log_text += f">m[{len(self.__messages)-1}]: {msg}\n"

        if self.__file_path != "" and self.__auto_save:
            self.save_log()
    
    def get_log_text(self) -> str:
        return self.__log_text
    
    def get_messages_list(self) -> list[str]:
        return self.__messages
    
    def get_message(self, index: int) -> str:
        return self.__messages[index]
    
    def set_log_file_path(self, path: str) -> None:
        self.__file_path = path

        if self.__file_path != "" and self.__auto_save:
            self.save_log()
    
    def save_log(self) -> None:
        if self.__file_path != "":
            with open(self.__file_path, "w") as fp:
                fp.write(self.__log_text)
    