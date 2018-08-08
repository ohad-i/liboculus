/******************************************************************************
 * This file has been derived from the original Blueprint Subsea
 * Oculus SDK file "SonarClient.h".
 *
 * The original Oculus copyright notie follows
 *
 * (c) Copyright 2017 Blueprint Subsea.
 * This file is part of Oculus Viewer
 *
 * Oculus Viewer is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Oculus Viewer is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *****************************************************************************/

#include <string.h>
#include <sstream>

#include <boost/bind.hpp>
#include <chrono>

#include "liboculus/SonarClient.h"

#include "g3log/g3log.hpp"

namespace liboculus {

using std::string;


// ----------------------------------------------------------------------------
// SonarClient - a listening socket for oculus status messages

SonarClient::SonarClient(boost::asio::io_service &context, uint32_t ip,
                          const std::shared_ptr<SimpleFireMessage> &fire )
  : _ipAddress( boost::asio::ip::address_v4(ip) ),
    _ioService(context),
    _socket(_ioService),
    _writeTimer(_ioService),
    _fireMessage(fire)
{
  doConnect();
}

SonarClient::SonarClient(boost::asio::io_service &context,
                          const boost::asio::ip::address &addr,
                          const std::shared_ptr<SimpleFireMessage> &fire )
  : _ipAddress( addr ),
    _ioService(context),
    _socket(_ioService),
    _writeTimer(_ioService),
    _fireMessage(fire)
{
  doConnect();

  CHECK( (bool)_fireMessage );
}

SonarClient::~SonarClient()
{

}

void SonarClient::doConnect()
{
  uint16_t _port = 52103;

  boost::asio::ip::tcp::endpoint sonarEndpoint( _ipAddress, _port);

  LOG(DEBUG) << "Connecting to sonar at " << sonarEndpoint;

  _socket.async_connect( sonarEndpoint, boost::bind(&SonarClient::connectHandler, this, _1) );
}


void SonarClient::connectHandler(const boost::system::error_code& ec)
{
  if (!ec) {

    startReader();

    // Send one packet immediately.  If successful, it will schedule the next one
    writeHandler( ec );

  } else {
    LOG(WARNING) << "Error on connect: " << ec.message();
  }
}

//== Data writers

void SonarClient::scheduleWrite()
{
  _writeTimer.expires_from_now(std::chrono::milliseconds(500));
  _writeTimer.async_wait(boost::bind(&SonarClient::writeHandler, this, _1));
}

void SonarClient::writeHandler(const boost::system::error_code& ec )
{
  if( !ec ) {
    boost::asio::streambuf msg;

    _fireMessage->serialize(msg);

    auto result = _socket.send( msg.data() );
    LOG(DEBUG) << "Sent " << result << " bytes to sonar";
  } else {
    LOG(WARNING) << "Error on write: " << ec.message();
  }

  // Schedule the next write
  scheduleWrite();
}

//=== Readers
void SonarClient::startReader()
{
  // Start an asynchronous receive
  // _socket.async_receive( boost::asio::buffer((void *)&_pingHeader, sizeof(OculusSimplePingResult)),
  //                         boost::bind(&SonarClient::readHeader, this, _1, _2));
}


void SonarClient::readHeader(const boost::system::error_code& ec, std::size_t bytes_transferred )
{
  if (!ec)
  {
    LOG(DEBUG) << "Got " << bytes_transferred << " bytes from sonar";

    startReader();
  }
  else
  {
    LOG(WARNING) << "Error on receive: " << ec.message();
  }
}

// void SonarClient::doReceiveStatusMessage()
// {
//   boost::asio::async_read(_socket,
//       boost::asio::buffer(read_msg_.data(), sizeof(OculusStatusMsg)),
//       [this](boost::system::error_code ec, std::size_t /*length*/)
//       {
//
//         if (!ec) {
//           read
//         } else {
//           _socket.close();
//         }
//       });
// }

// ----------------------------------------------------------------------------
// Signalled when there is data available in the socket buffer
// Note that if the Oculus Viewer software is running on a PC with two network ports then it is
// possible that both these ports will receive the status message
// In this case we will see twice as many status messages as expected
// void SonarClient::ReadDatagrams()
// {
//   // Read through any available datagrams
//   while (m_listener->hasPendingDatagrams())
//   {
//     // Read the datagram out of the socket buffer
//     QByteArray datagram;
//
//     datagram.resize(m_listener->pendingDatagramSize());
//     m_listener->readDatagram(datagram.data(), datagram.size());
//
//     // If datagra is of correct size, cast and signal any observers
//     if (datagram.size() == sizeof(OculusStatusMsg))
//     {
//       OculusStatusMsg osm;
//       memcpy(&osm, datagram.data(), datagram.size());
//
//       if (osm.hdr.oculusId == OCULUS_CHECK_ID)
//       {
//         m_valid++;
//
//         emit NewStatusMsg(osm, m_valid, m_invalid);
//       }
//     }
//     else
//     {
//       m_invalid++;
//     }
//   }
// }

}
