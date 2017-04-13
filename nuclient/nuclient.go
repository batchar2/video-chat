package nuclient

// Нуклиент - отдельная горутина, отвечающая за связь с удаленым сервером.

import (
	"fmt"
	"net"
	"octopus/conf"
	"octopus/netpackets"
	"octopus/request"
	//	"time"
)

type Nuclient struct {
	// Канал связи между нуклиентом и ядром
	ChanelClient2Nucleus chan NucleusPacketHeader
	// Сетевое соединение между нуклиентом и удаленым клиентом
	Connect net.Conn
	// Прямой канал связи между ядром и нуклиентом
	ChanelNucleus2Client chan NucleusPacketHeader
	// уникальный идентификатор Нуклиента. Используется для опознавания ядром системы
	NuclientUuid string
}

// Реализация взаимодействия между ядром системы и удаленым клиентом
func (nuclient *Nuclient) Start() {
	defer nuclient.Connect.Close()

	// канал для связи горутины, чтения данных, от клиента до нуклиента
	var chanelClientToNuclient = make(chan netpackets.ChanelPacketHeader, 100)
	// Канал извещает нулиента о завершении работы приложения
	var chanelIsConClose = make(chan bool)
	// Запускаю канал для связи с удаленным клиентом
	go clientReadData(nuclient.Connect, chanelClientToNuclient, chanelIsConClose)

	// инициализация обработчиков пакетов
	var requestProcessing = request.Request{}
	requestProcessing.Init()

	for {
		select {
		// Получены данные от удаленного клиента. Пускаю в обработку
		case chanelPacket := <-chanelClientToNuclient:
			go requestProcessing.Processing(chanelPacket.Binary(), chanelPacket.GetPacketType())
		// Получены данные от ядра системы
		case <-nuclient.ChanelNucleus2Client:
			fmt.Println("Получены данные от ядра системы")
		// информировнаие о закрытии соединения с удаленным клиентом
		case <-chanelIsConClose:
			return
			/* закрыть соединение по истечению заданого времени
			case <-time.After(time.Second * conf.CLOSE_CONNECTION_CLIENT_AFTER_SECONDS):
			case <-time.After(time.Second * 5):
				fmt.Println("Время вышло")
				return
			*/
		}
	}
}

// Читаем данные из сокета
func clientReadData(conn net.Conn, chanelData chan<- netpackets.ChanelPacketHeader, chanelIsConClose chan<- bool) {
	for {
		var buf = make([]byte, conf.PACKET_SIZE)
		_, err := conn.Read(buf)

		if err != nil {
			fmt.Println("Сокет закрыт")
			fmt.Print(err)
			chanelIsConClose <- true
			return
		}

		// Произвожу парсинг данных и строю пакет на основе этих данных
		var packet = netpackets.ChanelPacketHeader{}
		packet.ParseBinaryData(buf)

		// Отличаю от мусорных данных и отпарвляю в канал на обработку нуклиенту
		if packet.GetMagicNumber() == conf.MAGIC_NUMBER {
			chanelData <- packet
		}

	}
}
