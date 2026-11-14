// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AIRecord
/// @notice Stores the most recent sentiment-analysis record (text + label).
/// @dev Each call to saveRecord overwrites the previous record. Access is not
///      restricted: anyone can call saveRecord. This is a testnet demo contract.
contract AIRecord {
    struct Record {
        string text;
        string sentiment;
    }

    Record public latestRecord;

    function saveRecord(string memory _text, string memory _sentiment) public {
        latestRecord = Record(_text, _sentiment);
    }

    function getRecord() public view returns (string memory, string memory) {
        return (latestRecord.text, latestRecord.sentiment);
    }
}
