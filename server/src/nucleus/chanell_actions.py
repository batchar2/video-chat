import ctypes
import logging

from abc import ABC, abstractmethod

from .packets import default_options as op 

from .packets import chanell_level as chanel

class Action(ABC):
    """ Класс "команда", реализует вызов функции. Используется для связи с клиентом """
    _related_object = None 
    
    def __init__(self, *, related_object=None):
        """
        Конструктор класса, реализует логику обработки пакета
        :param related_object: Ссылка на связанный объект, через который происходит обмен с ядром 
        """
        self._related_object = related_object


    def __call__(self, *, packet=None):
        """
        Вызывается где-то. Таким оразом разделяем логику работу 
        :param packet: тело пакета    
        """
        pass


    @property
    def related_object(self):
        return self._related_object



class ActionTypeNormal(Action):
    """  Обработка "нормального"" пакета """
    def __init__(self, *, related_object=None):
        super(ActionTypeNormal, self).__init__(related_object=related_object)

    def __call__(self, *, packet=None):
        logging.info('Обрабатываем данный пакет ActionTypeNormal. Хочу преобразовать в сетевой')


class ActionTypeQOS(Action):
    """  Обработка "нормального" пакета """
    def __init__(self, *, related_object=None):
        super().__init__(related_object=related_object)

    def __call__(self, *, packet=None):
        pass



class ActionTypeClientSendPublicKey(Action):
    """  Обработка пакета с публичным ключем клиента """
    def __init__(self, *, related_object=None):
        super().__init__(related_object=related_object)

    def __call__(self, *, packet=None):
        """ Получаю от клиента открытый ключ, и генерирую свой """

        self.related_object.set_client_public_key(key=packet.key)
        self.related_object.generate_rsa_keys()
        
        public_key = self.related_object.get_public_key()

        # строку в массив байт
        str2cubytes = lambda s, size: ctypes.cast(s, ctypes.POINTER(ctypes.c_ubyte * size))[0]

        ans_packet = chanel.ChanelLevelPacketKeyAuth()
        ans_packet.magic_number = op.MAGIC_NUMBER
        ans_packet.version = op.CHANEL_PACKET_VERSION
        ans_packet.type = op.CHANEL_PACKET_TYPE_PUBLIC_KEY_SERVER_CLIENT_EXCHANGE
        ans_packet.key = str2cubytes(public_key, op.CHANEL_PACKET_AUTH_BODY_SIZE) #str2cubytes(public_key, op.CHANEL_PACKET_AUTH_BODY_SIZE)
        ans_packet.length = len(public_key)

        self.related_object.send_user(packet=ans_packet)