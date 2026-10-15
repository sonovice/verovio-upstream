#include "customtuning.h"
#include "doc.h"

#include <cassert>
#include <fstream>
#include <iterator>
#include <utility>

int main(int argc, char **argv)
{
    assert(argc == 3);
    std::ifstream input(argv[2]);
    const std::string definition((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
    vrv::Doc doc;
    doc.GetResourcesForModification().SetPath(argv[1]);

    vrv::CustomTuning empty;
    assert(!empty.IsValid());
    const vrv::CustomTuning constEmpty;
    assert(constEmpty.GetTuning().notationMapping.count == 0);
    // Mutable access to a default tuning was supported before lazy allocation.
    empty.GetTuning() = Tunings::Tuning(Tunings::parseASCLData(definition));
    assert(empty.IsValid());

    vrv::CustomTuning original(definition, &doc, false);
    assert(original.IsValid());
    assert(original.GetTuning().notationMapping.count == 24);
    vrv::CustomTuning copy(original);
    assert(copy.IsValid());
    assert(&copy.GetTuning() != &original.GetTuning());
    const auto first = original.GetNoteMap().begin()->first;
    const auto value = original.GetNoteMap().at(first);
    copy.GetNoteMap()[first] = "independent";
    assert(original.GetNoteMap().at(first) == value);

    vrv::CustomTuning assigned;
    assigned = original;
    assert(assigned.IsValid());
    assert(&assigned.GetTuning() != &original.GetTuning());
    vrv::CustomTuning moved(std::move(copy));
    assert(moved.IsValid());
    assert(!copy.IsValid());
    copy = std::move(assigned);
    assert(copy.IsValid());
    assert(!assigned.IsValid());
    assigned = vrv::CustomTuning();
    moved = assigned;
    assert(!moved.IsValid());
    auto &self = original;
    original = self;
    original = std::move(self);
    assert(original.IsValid());
    vrv::CustomTuning invalid("not an ASCL tuning", &doc, false);
    assert(!invalid.IsValid());
}
