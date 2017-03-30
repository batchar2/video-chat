import ctypes
import logging

from abc import ABC, abstractmethod

from .netpackets import options as op 
from .netpackets import chanel

#from .nucpackets import packets as nucpackets
#from .nucpackets import options as nop

from .. import options as bopt

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

        #self.related_object.set_client_public_key(key=packet.key)
        self.related_object.generate_rsa_keys()
        
        public_key = self.related_object.get_public_key()

        

        # строку в массив байт
        
        str2cubytes = lambda s, size: ctypes.cast(s, ctypes.POINTER(ctypes.c_ubyte * size))[0]

        ans_packet = chanel.ChanelLevelPacketKeyAuth()
        ans_packet.magic_number = bopt.MAGIC_NUMBER
        ans_packet.version = op.CHANEL_PACKET_VERSION
        ans_packet.type = op.CHANEL_PACKET_TYPE_PUBLIC_KEY_SERVER_CLIENT_EXCHANGE
        #ans_packet.key = str2cubytes(public_key, op.CHANEL_PACKET_AUTH_BODY_SIZE) 
        ans_packet.length = len(public_key)

        self.related_object.send_user(packet=ans_packet)
        


class ActionTypeClientSendPrivateKey(Action):
    """  Обработка пакета с закрытым симетричным ключем клиента. Зашифрован открытым ключем сервера """
    def __init__(self, *, related_object=None):
        super().__init__(related_object=related_object)


    def __call__(self, *, packet=None):
        """ Получаю от клиента пакет.
            Расшифровываю своим закрытым ключем
            Сохраняю секретный симетричный ключ клиента
        """
        #data = self.related_object.decode_rsa_data(data=packet.key)
        #self.related_object.set_client_aes_key(key=packet.key)
        data = self.related_object.decode_rsa_data(data=None)
        self.related_object.set_client_aes_key(key=None)

        # Отвечаю клиенту на принятие данных
        ans_packet = chanel.ChanelLevelPacketKeyAuth()
        ans_packet.magic_number = bopt.MAGIC_NUMBER
        ans_packet.version = op.CHANEL_PACKET_VERSION
        ans_packet.type = op.CHANEL_PACKET_TYPE_PRIVATE_KEY_EXCHANGE_SUCCESS

        self.related_object.send_user(packet=ans_packet)


class ActionTypeClientAuth(Action):
    """ Принятие логина и пароля от пользователя.
        Зашифрованы симетричным ключем
    """
    def __init__(self, *, related_object=None):
        super().__init__(related_object=related_object)

    def __call__(self, *, packet=None):
        """ Получаю от клиента пакет.
            Расшифровываю симетричным ключем
            Отправляю ядру на верификацию
            Ответ придет позже, асинхронно (еще не сделано)
        """

        logging.info('ПЫТАЮСЬ АВТОРИЗОВАТЬ ПОЛЬЗОВАТЕЛЯ')
        
        username = None #self.related_object.decode_aes(data=packet.username)
        password = None #self.related_object.decode_aes(data=packet.password)

        # Перенаправляю запрос другому клиенту (ядра) !!!!
        """ Тут не должно быть этого кода
        nuc_packet = nucpackets.NuPacketRequestAuth()
        nuc_packet.magic_number = bopt.MAGIC_NUMBER

        nuc_packet.username = username
        nuc_packet.password = password
        nuc_packet.type = nop.NUC_AUTH_REQUEST
        
        self.related_object.request_nucleus(packet=nuc_packet)
        

        """
        